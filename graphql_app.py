from strawberry.asgi import GraphQL

from weather_assistant.graphql_schema import create_schema

app = GraphQL(create_schema())
