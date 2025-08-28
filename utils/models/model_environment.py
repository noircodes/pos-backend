from enum import Enum


class EnvironmentEnum(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"