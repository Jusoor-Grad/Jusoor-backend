"""
Mocking module for core models.
"""
import email
from faker import Faker
from .models import  Therapist, StudentPatient, KFUPMDepartment
from authentication.models import User


faker = Faker('en')

class UserMock:
    
    @staticmethod
    def mock_instances(n: int):
        
        users = []

        for _ in range(n):
            users.append(
                User.objects.create_user(
                    username= faker.name(),
                    email = faker.ascii_free_email(),
                    password= faker.password(length=12),
                    is_active=True,
                    first_name = faker.first_name(),
                    last_name=faker.last_name(),

                )
            )
        
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
                    bio= faker.paragraph(),
                    specialty = faker.paragraph(n_sentences=1)
                )
            )

        return Therapist.objects.bulk_create(therapists)



class PatientMock:
    

    def mock_instances(n: int):

        patients = []
        random_departments

