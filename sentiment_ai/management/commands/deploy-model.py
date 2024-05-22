from django.core.management.base import BaseCommand, CommandParser
from sagemaker.huggingface import HuggingFaceModel
import boto3
import sagemaker
class Command(BaseCommand):

    help = "Deploy a model hosted on specified S3 bucket to AWS SageMaker for inference"



    def add_arguments(self, parser: CommandParser) -> None:
        
        parser.add_argument('model-data', type=str, help='The S3 path to the model tar.gz file')
        parser.add_argument('role', type=str, help='The IAM role to use for the SageMaker model')
        parser.add_argument('transformers-version', type=str, help='The S3 bucket where the model is stored', default="4.26.0")
        parser.add_argument('pytorch-version', type=str, help='The S3 bucket where the model is stored', default="1.13.1")
        parser.add_argument('py-version', type=str, help='The S3 bucket where the model is stored', default="py39")
        parser.add_argument("instance_type", type=str, help="The instance type to deploy the model to", default="ml.t2.medium")
        parser.add_argument("instance-count", type=int, help="The number of instances to deploy the model to", default=1)
        
    def handle(self, *args, **options):

        
        sess = sagemaker.Session()

        model = HuggingFaceModel(
            model_data=options['model-data'],
            role=options['role'],
            transformers_version=options['transformers-version'],
            pytorch_version=options['pytorch-version'],
            py_version= options['py-version'],
        )
        
        predictor = model.deploy(
            initial_instance_count=options['instance_count'],
            instance_type=options['instance_type']
        )

        data = {
            "inputs": "I went out with my friends to a nice restautrant"
        }

        print(predictor.predict(data))

