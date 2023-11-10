use crate::Result;
use mwbot::Bot;

const PKG_VERSION: &str = env!("CARGO_PKG_VERSION");

fn user_agent() -> String {
    format!("EarwigCVDetector/{}", PKG_VERSION)
}

pub struct Site {
    project: String,
    lang: String,
}

impl Site {
    pub fn new<S: ToString>(project: S, lang: S) -> Self {
        Site {
            project: project.to_string(),
            lang: lang.to_string(),
        }
    }

    fn domain(&self) -> String {
        format!("{}.{}.org", self.lang, self.project)
    }

    pub async fn bot(&self) -> Result<Bot, mwbot::ConfigError> {
        let domain = self.domain();
        Bot::builder(
            format!("https://{}/w/api.php", domain),
            format!("https://{}/api/rest_v1", domain),
        )
        .set_user_agent(user_agent())
        .build()
        .await
    }
}
