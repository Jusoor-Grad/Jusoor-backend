
# Overview
Jusoor. A plural of "Bridge" in Arabic, is a platform for management of mental health appointments equipped with dynamic survey builder, and AI-driven therapist support system targeted at KFUPM students

## Appendix
- [Used Technologies](#used-technologies)
- [Project Structure](#project-structure)
- [Application Structure](#application-structure)
- [How to run the project for development](#how-to-run-the-project-locally)
- [How to deploy for production](#how-to-deploy-the-project-for-production)
- [Limitations](#limitations)

# Used Technologies

Jusoor Backend depends on a myriad of amazing open-source technologies that empower its system

- `django` for main HTTP server handling and Database ORM
- `django-rest-framework` easy-to-use wrapper for building HTTP APIs on top of `django`
- `djangorestframework-simplejwt` utility for creation and management of user JWTs in conjunction with `django-rest-framework`
- `drf-yasg`: OpenAPI swagger/redoc API documentation generation
- `django-filter`: utility for django ORM-based HTTP query parameter filtering
- `celery/django-celery-results`: background task execution handling with `redis` backend
- `pydantic`: typesafe type-hints for business logic and cross-app communications
- `langchain`: easy-to-use abstraction layer when using third-party LLMs as `openai`
- `faker`: utility used to easily generate mocked values for end-2-end testing
- `sagemaker`: AWS SDK to deploy AI models to your AWS account
- `channels`: Django Async server and WebSocket support for Django
- `PostgreSQL`: Database engine

# Project structure
Jusoor follows standard django app-based directory structure with the following main directories
- `appointments`: Patient Appointment scheduling and Therapist working hour availability management
- `authentication`: user authentication and authorization, along some hashing and encryption utilities
- `chat`: LangChain-based LLM chatbot on top of a `pgvector` based RAG for interacting with student patients
- `core`: a collection of utilies for DRF class viewset enhancement like action-based permissions and dynamically scopes querysets. formatted HTTP response,
and soft-deleted querysets
- `sentiment_ai`: serving of sentiment and mental disorder reports using deployed AI models
- `django-extensions`: a utility set for easier development like `shell_plus` interactive notebook terminal interface and many more

# Application structure
Each application is structured uniformly and may contain the following files:
- `view.py` definition of HTTP endpoints along serialization, permission and queryset scoping configurations
- `models.py` schema definition of the application using Django's ORM
- `tasks.py` definition of Celery background tasks
- `serializers.py` definition of DRF HTTP payload and resposne serialization
- `tests.py` file containing all the created unit tests for the app
- `types.py` custom pydantic types used to ensure type-safety and minimize bugs in business logic
- `mock.py` utilities dedicated to mock a group of related ORM objects for easier
unit and end-2-end testing
- `enums.py` constants to be used in business logic and schema field validation choices
- `urls.py` routing configuration for HTTP endpoints defined in `views.py`

# How to run the project locally
1. Install the python dependencies from the `Pipfile` (using `pipenv` is recommended to preserve used versioning, but you can use other dependency managers like `poetry`)
```bash
pipenv install
```
2. add the following environmental variables as shown in `.env.example`
> [!WARNING]
> You must add the populated environmental variables in a new file named `.env` to be able to run the application

3. run the migrations after configuring your database settings
```bash
python manage.py migrate
```

4. upload model weights in the `/model_weights` directory to AWS SageMaker and deploy it with the following configuration command
```bash
python manage.py deploy-model --model-data <s3-model-artifact-path> --role <configured-sagemaker-role>
```

> [!NOTE]
> You need to have a valid IAM role to execute needed SageMaker actions to deploy the model. More info [here](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html). Deploying on other platforms is also possible, but it requires updating the interfacing classes on `sentiment_ai/agents` directory

5. run the main server process
```bash
python manage.py
```

6. spawn a redis instance to be used for background task scheduling and caching
```bash
docker run --rm -p 6379:6379 redis:7
```

> [!NOTE]
> Make sure that docker is running on your device, before running the command!

7. run a `celery` process on a second terminal to start handling async tasks using the currently spawned `redis` for cross-process communication (I use `watchdog` to continue refreshing the process on every application source code update)
```bash
watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A jusoor_backend worker -l INFO -P solo
```
> [!INFO]
> to the chatbot. Make sure to create a new DB record with specified prompt, and supply its ID to the chatbot wrapper class, as the current implementation uses relies on a dynamic DB-stored chatbot configuration when using the chatbot

After running the main process, you can find the swagger API docs at [localhost:8000/swagger/](localhost:8000/swagger/)



# How to deploy the project for production
- App server: The deployment configuration supplied works seemlessly with Heroku using `Pipfile` to specify needed dependencies, and `Procfile` to specify 2 processes for main HTTP server and background tasks
- Database: You can use any database provider. Make sure that the DB dialect supports `JSON/JSONB` fields (I personally recommend using `PostgreSQL`)
- AI models: I recommend using AWS SageMaker, with the configured command `deploy-model`
- Background task scheduling: You need to provision a Redis instance to be used for Caching, WebSocket connection handling, as well as Background task execution.

## Limitations
- Both Emotion and Mental disorder models can only work on `English` language, and are trained on relatively long text passages (Reddit posts), which can hinder their performance on normal short chat message texts
- The reporting endpoint can take first 15 chat messages max from the specified time frame to avoid overwhelming the repoerting LLM context window
- We implemented minimal measrues to avoid abusing the chatbot system prompt, but a dedicated text abuse classifier pipeline would be more suitable for handling such task
- unit tests are available for only `/appointments` and `/surveys` apps
