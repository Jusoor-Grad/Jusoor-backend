import faker
from authentication.models import User
from faker import Faker
from django.contrib.auth import get_user_model
from chat.models import ChatBot, ChatMessage

faker = Faker()

class ChatBotMocker:

    def mock_instances(n: int):

        bots = []
        for i in range(n):
            # create a user profile
            user = User.objects.create_user(
                username = faker.name(),
                email = faker.email(),
                password = faker.password()
            )

            bots.append(ChatBot(
                user_profile=user,
                name=faker.name(),
                temperature= faker.random.random(),
                max_response_tokens=faker.random.randint(200, 300),
                model_name= 'gpt-3.5-turbo',
                top_p=faker.random.random(),
                captured_history_length=faker.random.randint(5, 20),
                prompt=faker.text()
            ))

        return ChatBot.objects.bulk_create(bots)

class ChatMessageMocker:

    @staticmethod
    def mock_instances(n_msg_pairs: int, user: User, bot: ChatBot):

        messages = []
        for i in range(2*n_msg_pairs):
            messages.extend([ChatMessage(
                content=faker.text(),
                sender=user,
                receiver=bot.user_profile,
                
            ),
            ChatMessage(
                content=faker.text(),
                sender=bot.user_profile,
                receiver=user,
                
            )])

        return ChatMessage.objects.bulk_create(messages)
            

