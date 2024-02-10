from os import name
from typing import Any, List, Dict, Union
from django.db.models import QuerySet, Q
from django.utils import timezone
from numpy import isin
from rest_framework.generics import GenericAPIView
from django.contrib.auth import get_user_model
from core.enums import PATIENT_PROFILE_FIELD, QuerysetBranching, UserRole
from abc import ABC, abstractmethod

class SoftDeletedQuerySet(QuerySet):
    """
        Overriding standard queryset to remove all softly deleted records
    """

    def delete(self):
        """
        Overriding the default delete method to soft delete the objects
        """
        return super(SoftDeletedQuerySet, self).update(deleted_at=timezone.now())

    def hard_delete(self):
        """
        Method to permanently delete the objects from the database
        """
        return super(SoftDeletedQuerySet, self).delete()

        

# ---------------- Utilities for QS mapping
class QSExtractor:
    """
        Utility class used to extract the quertset either directly or through invoking
        the passed queryset mapper
    """

    def _extract_qs(self, view: GenericAPIView, qs: Union[QuerySet, 'QSWrapperFilter']) -> QuerySet:
        """
            Extra querysets from the passed queryset mapper or simply return 
            the vanilla queryset object in the same call stack level

            @param view: the view instance to supply the request information for filtering for next levels
            @param qs: the queryset to be filtered or another nested dynamic queryset mapper
        """

        

        if callable(qs):
            return qs(view, qs)
        elif isinstance(qs, QuerySet):
            return qs
        else:
            raise ValueError('Invalid queryset/mapper definition') 


class QSWrapperFilter(ABC, QSExtractor):
    """
        Utility class used for conditional queryset mapping
    """

    def __init__(self, mapper: Dict[UserRole, Q], pass_through: List[str] = None) -> None:
        """
            @mapper: dictionary to specify mapping conditions to queryset filters
            @passthrough: list of keys used to determine whether the queryset should be passed through without filtering

            NOTE: the strings used as the mapper keys should include information retrivevable from the
            passed DRF viewset object instance
        """

        self.mapper = mapper
        self.pass_through = pass_through

    @abstractmethod
    def _pass_qs_or_reject(self, view: GenericAPIView, qs: Union[QuerySet, 'QSWrapperFilter'], *args, **kwargs) -> QuerySet:
        pass

    @abstractmethod
    def __call__(self, view: GenericAPIView, qs: Union[QuerySet, 'QSWrapperFilter'], *args: Any, **kwds: Any) -> QuerySet:
        """
            starting dynamic recursive queryset filtering on request-time

            @view: the view instance to supply the request information for filtering
            @qs: the queryset to be filtered or another nested dynamic queryset mapper
            @passthrough: list of values whoe values determine whether the queryset should be passed completely through
        """
        pass

class QSWrapperBranch(QSWrapperFilter):


    
    def _map_filter_qs(self, view: GenericAPIView, qs: Union[QuerySet, 'QSWrapperFilter'], lookup_key: str) -> QuerySet:
        """
            utility used to filter the existing queryset object based
            on a string -> Q() object OR a QSWrapperFilter mapping object stored in the instance before hand
            
        """
        
        # if the value of the mapper is a Q object, use it to filter the queryset
        if isinstance(self.mapper[lookup_key], Q):
            return self._extract_qs(view, qs).filter(self.mapper[lookup_key])
        
        # if the value of the mapper is a QSWrapperFilter object, invoke it to filter the queryset
        elif isinstance(self.mapper[lookup_key], QSWrapperFilter):
            return self.mapper[lookup_key](view, qs)

        raise ValueError('Invalid mapper object')           


class OwnedQS(QSWrapperFilter):
    """
        Queryset filter action that only returns owned objects by the current user
    """

    def __init__(self, ownership_fields: List[str] = ['user'], user_model_rel: str = None) -> None:
        """
            @param ownership_field: the field name used on the resource object to determine the ownership
            @param user_model_rel: the name of the attribute of the user model used for ownership determination
        """

        if len(ownership_fields) == 0:
            raise ValueError('One ownership field must be specified')

        self.ownership_fields = ownership_fields
        self.user_model_rel = user_model_rel

    def _pass_qs_or_reject(self, view: GenericAPIView, qs: Union[QuerySet, QSWrapperFilter]) -> QuerySet:
        return self._extract_qs(view, qs).none()

    def __call__(self, view: GenericAPIView, qs: Union[QuerySet, QSWrapperFilter], *args: Any, **kwds: Any) -> QuerySet:

        user = view.request.user

        # checking if a custom user model field is used for ownership determination
        if self.user_model_rel is not None:

            # if the user object does not have the specified attribute, return an empty queryset
            ## in Django ORM terms, this means that the user does not own any records of the target model
            if not hasattr(user, self.user_model_rel):
                return self._pass_qs_or_reject(view, qs)
            
            user = getattr(user, self.user_model_rel)

        # filtering the passed queryset based on the ownership field
        filters = Q(**{self.ownership_fields[0]: user})
        if len(self.ownership_fields) > 1:
            for field in self.ownership_fields[1:]:
                filters |= Q(**{field: user})

        return self._extract_qs(view, qs).filter(filters)
        

class PatientOwnedQS(OwnedQS):
    """
        shotcut to use querysets owned by a patient
    """

    def __init__(self, ownership_fields: List[str] = [UserRole.PATIENT.value]) -> None:
        super().__init__(ownership_fields=ownership_fields, user_model_rel=PATIENT_PROFILE_FIELD)

class TherapistOwnedQS(OwnedQS):
    """
        shotcut to use querysets owned by a therapist
    """
    def __init__(self, ownership_fields: List[str] = [UserRole.THERAPIST.value]) -> None:
        super().__init__(ownership_fields= ownership_fields, user_model_rel=PATIENT_PROFILE_FIELD)

class UserGroupQS(QSWrapperBranch):
    """Queryset mapper based on user group membership"""


    def _pass_qs_or_reject(self, view: GenericAPIView, qs: Union[QuerySet, QSWrapperFilter], *args, **kwargs) -> QuerySet:

        user = view.request.user
        
        if kwargs.get('user_groups') is None:
            raise ValueError('User groups not passed to qs pasthrough handler')
        
        user_groups = kwargs.get('user_groups')

        if user_groups.filter(name__in=self.pass_through).exists():
            return self._extract_qs(view, qs)
        else:
            return self._extract_qs(view, qs).none()

    def __call__(self, view: GenericAPIView, qs: Union[QuerySet, QSWrapperFilter], *args: Any, **kwds: Any) -> QuerySet:
        user = view.request.user

        user_groups = user.groups.filter(name__in= list(self.mapper.keys()) + self.pass_through)
        
        # if the user has a passthrough group, return the queryset as is with no filtering
        if user_groups.filter(name__in=self.pass_through).exists():
            return self._extract_qs(view, qs)
        
        # if there is no match with any specified user groups, return an empty queryset
        if not user_groups.exists():
            return self._pass_qs_or_reject(view, qs, user_groups=user_groups)

        else:
            # NOTE: the order of group keys matters
            for key in self.mapper.keys():
                if user_groups.filter(name=key).exists():
                    return self._map_filter_qs(view, qs, lookup_key=key)

        raise ValueError('Unexpcted output of conditional queryset mapping')

class PermissionQS(QSWrapperBranch):
    """Queryset mapper based on user permissions"""

    def __call__(self, view: GenericAPIView, qs: Union[QuerySet, QSWrapperFilter], *args: Any, **kwds: Any) -> QuerySet:
        
        user = view.request.user
        user_permissions = user.get_all_permissions()
        # if the user has a passthrough permission, return the queryset as is with no filtering
        if set(user.get_all_permissions()) & set(self.pass_through):
            return self._extract_qs(view, qs)

        if not set(user.get_all_permissions()) & set(self.mapper.keys()):
            return self._pass_qs_or_reject(view, qs)

        else:
            # NOTE: the order of permission keys matters
            for key in self.mapper.items():
                if user.has_perm(key):
                    return self._map_filter_qs(view, qs, lookup_key=key)

        raise ValueError('Unexpcted output of conditional queryset mapping')




class QSWrapper:
    """
        Wrapper class to abstract the dynamic queryset mapping
        for DRF viewsets
    """

    def __init__(self, queryset: QuerySet) -> None:    
        self.queryset = queryset
        # used to track all the queryset mapper instances in the stack
        self.mapper_stack: List[QSWrapperFilter] = []
        # used to track all keys used by each chained mapper
        self.mapper_keys_stack: List[List[str]] = []

        self.mapper_prequisites: List[str] = []

        if not callable(self.queryset) and not isinstance(self.queryset, QuerySet):
            raise ValueError('Queryset must be a callable or a Queryset instance')


    def _get_queryset(self, view: GenericAPIView) -> QuerySet:
        """
            Method used to either return raw queryset or successively apply
            all the queryset mappers in the stack to filter it dynanamically
        """

        if not self.mapper_stack:
            return self.queryset

        qs = self.queryset
        for mapper in self.mapper_stack:
            qs = mapper(view, qs)

        return qs
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        
        def __wrapper__(view: GenericAPIView):
            return self._get_queryset(view)

        return __wrapper__

    def _get_last_prerequisites(self) -> List[str]:
        """
            Method to return the keys used by the last mapper in the stack
        """

        if  len(self.mapper_keys_stack) == 0:
            return []

        return self.mapper_keys_stack[-1]
    
    def _validate_mapper_keys(self, keys: List[str]):
        """
            Function used to check for the validity of the passed keys
            using the last mapper's keys
        """

        last_mapper_keys = self._get_last_prerequisites()

        print('LAST MAPPER KEYS', last_mapper_keys, '\nPASSED KEYS',  keys)
        
        if not all([key in last_mapper_keys for key in keys]) and len(last_mapper_keys) > 0:
            raise ValueError('Invalid keys passed for filtering')


    def branch(self, qs_mapper: Dict[str, Union[Q, QSWrapperFilter]], by: QuerysetBranching, pass_through: List[str] = []) -> 'QSWrapper':
        """
            Method to used to add a new queryset mapper to the stack
            for dynamic length branching for a queryset

            @param mapper: the mapper object to be used for filtering
            @param by: the type of branching to be used
            @param passthrough: list of values whoe values determine whether the queryset should be passed completely through
        """

        # appending the mapper object to the stack
        if by == QuerysetBranching.USER_GROUP:
            self.mapper_stack.append(UserGroupQS( qs_mapper, pass_through=pass_through))
        elif by == QuerysetBranching.PERMISSION:
            self.mapper_stack.append(PermissionQS(qs_mapper, pass_through=pass_through))
        else:
            raise ValueError('Invalid branching type')

        # appending the keys of the mapper to the stack to be used for chained filtering
        self.mapper_keys_stack.append(list(qs_mapper.keys()) + pass_through)

        return self ## used for future chaining





