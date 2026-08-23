from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    predict_api_key: str = ''
    predict_base_url: str = 'https://api.predict.fun'
    watch_wallets: str = ''
    category_allowlist: str = 'esports,politics'
    poll_seconds: int = 15
    paper_trading: bool = True
    live_trading: bool = False
    max_copy_usd: float = 50.0
    max_wallet_exposure_usd: float = 250.0
    max_daily_loss_usd: float = 100.0
    min_whale_score: float = 70.0
    min_sample_trades: int = 30
    arb_min_net_edge: float = 0.008
    polymarket_gamma_url: str = 'https://gamma-api.polymarket.com'

    @property
    def wallets(self) -> list[str]:
        return [x.strip().lower() for x in self.watch_wallets.split(',') if x.strip()]

    @property
    def categories(self) -> set[str]:
        return {x.strip().lower() for x in self.category_allowlist.split(',') if x.strip()}
