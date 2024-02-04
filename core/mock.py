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

        for i in range(n):
            email = faker.ascii_free_email()
            password= faker.password(length=12)

            print(email, password)
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
                    bio= faker.paragraph(),
                    speciality = faker.paragraph(nb_sentences=1)
                )
            )

        return Therapist.objects.bulk_create(therapists)



class PatientMock:
    
    @staticmethod
    def mock_instances(n: int):

        patients = []
        random_department = KFUPMDepartment.objects.all().order_by('?').first()
        users = UserMock.mock_instances(n=n)

        for i in range(n):
            patients.append(
                StudentPatient(
                    user=users[i],
                    department = random_department,
                    entry_date = faker.date_this_decade()
                )
            )
        
        return StudentPatient.objects.bulk_create(patients)

TherapistMock.mock_instances(2) # mock 10 patients