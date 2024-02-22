"""
Mocking module for core models.
"""
import email
from faker import Faker

from core.enums import UserRole
from .models import  Therapist, StudentPatient, KFUPMDepartment
from authentication.models import User
from django.contrib.auth.models import Group

faker = Faker('en')

class UserMock:
    
    @staticmethod
    def mock_instances(n: int):
        
        users = []

        for i in range(n):
            email = faker.ascii_free_email()
            password= faker.password(length=12)

            users.append(
                User.objects.create_user(
                    username= faker.name(),
                    email=email,
                    password=password,
                    is_active=True,
                    first_name = faker.first_name(),
                    last_name=faker.last_name()
                    ))
            
            
        
        return users


class TherapistMock:
    
    def mock_instances(n: int):

        # 1. mock user objects
        users = UserMock.mock_instances(n=n)

        therapists = []
        for user in users:

            therapists.append(
                Therapist(
                    user=user,
                    bio= faker.paragraph()
                )
            )

        therapists = Therapist.objects.bulk_create(therapists)

        gr , _= Group.objects.get_or_create(name=UserRole.THERAPIST.value)
        for therapist in therapists:
            gr.user_set.add(therapist.user)
        
        gr.save()

        return therapists



class PatientMock:
    
    @staticmethod
    def mock_instances(n: int):

        patients = []
        random_department = KFUPMDepartment.objects.all().order_by('?').first()
        users = UserMock.mock_instances(n=n)
        gr, _ = Group.objects.get_or_create(name=UserRole.PATIENT.value)

        for i in range(n):
            patients.append(
                StudentPatient(
                    user=users[i],
                    department = random_department
                )
            )
        
        students = StudentPatient.objects.bulk_create(patients)

        for student in students:
            gr.user_set.add(student.user)
        gr.save()

        return students

# TherapistMock.mock_instances(1) # mock 10 patients