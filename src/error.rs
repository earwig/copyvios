use thiserror::Error as ThisError;

pub type Result<T, E = Error> = std::result::Result<T, E>;

#[non_exhaustive]
#[derive(ThisError, Debug)]
pub enum Error {
    #[error("API error: {0}")]
    ApiError(#[from] mwapi::Error),
    #[error("Bot error: {0}")]
    BotError(#[from] mwbot::Error),
    #[error("Config error: {0}")]
    ConfigError(#[from] mwbot::ConfigError),
    #[error("Unable to find background image: {0}")]
    BackgroundError(String),
    // add nobackgroundserror, backgroundunavailableerror....
}
