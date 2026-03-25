from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 현재파일을 의미, 현재파일의 경로를 얻어냄(core), ** 현재파일의 부모파일들 중 첫번째 파일(app)/.env **
DOTENV_PATH = Path(__file__).resolve().parents[1] / ".env"   #app/.env의미함

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV_PATH,env_file_encoding="utf-8")
    db_user:str
    db_pwd:str
    db_name:str
    db_ip:str
    db_port:str
    
    @property
    def db_url(self) -> str:
        return f"mysql+aiomysql://{self.db_user}:{self.db_pwd}@{self.db_ip}:{self.db_port}/{self.db_name}"

config = Config() # 이때 Config가 생성되면서 .env파일을 읽어서 설정값들이 로드됨!