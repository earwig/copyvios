mod background;
mod error;
mod site;

pub use error::{Error, Result};

use crate::background::Background;
use askama::Template;
use axum::{routing::get, Router};
use std::net::SocketAddr;
use tower_http::services::ServeDir;
use tracing_subscriber::filter::LevelFilter;
use tracing_subscriber::EnvFilter;

#[tokio::main]
async fn main() {
    let filter = EnvFilter::builder()
        .with_default_directive(LevelFilter::INFO.into())
        .from_env()
        .expect("invalid RUST_LOG value");
    tracing_subscriber::fmt().with_env_filter(filter).init();

    let app = Router::new()
        .route("/", get(index))
        .route("/api", get(api))
        .route("/language", get(language))
        .route("/settings", get(settings))
        .nest_service("/static", ServeDir::new("static"));

    let addr = SocketAddr::from(([127, 0, 0, 1], 8080));
    tracing::info!("listening on {}", addr);
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}

#[derive(Template)]
#[template(path = "index.html")]
struct IndexTemplate {
    background: Background,
}

async fn index() -> IndexTemplate {
    let background = background::get_background()
        .await
        .expect("failed to get background image"); // TODO: handle gracefully
    IndexTemplate { background }
}

async fn api() -> &'static str {
    "TODO"
}

async fn language() -> &'static str {
    "TODO"
}

async fn settings() -> &'static str {
    "TODO"
}
