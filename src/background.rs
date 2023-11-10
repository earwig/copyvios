use crate::{site::Site, Error, Result};
use mwapi_responses::prelude::*;
use mwbot::{parsoid::WikinodeIterator, Bot, Page};
use rand::seq::SliceRandom;

pub struct Background {
    pub image_url: String,
    pub source_url: String,
}

async fn get_potd_images(bot: &Bot) -> Result<Vec<Page>> {
    let page = bot.page("User:The Earwig/POTD")?;
    let html = page.html().await?.into_mutable();

    let mut images = Vec::new();
    for link in html.filter_links() {
        let target = bot.page(&link.target())?;
        if !target.is_file() {
            continue;
        }
        images.push(target);
    }

    Ok(images)
}

#[query(prop = "imageinfo", iiprop = "url|size|canonicaltitle")]
pub(crate) struct InfoResponse {}

async fn get_background_from_page(bot: &Bot, image: &Page) -> Result<Background> {
    let mut resp: InfoResponse =
        mwapi_responses::query_api(&bot.api(), [("titles", image.title())]).await?;
    let info = resp
        .query
        .pages
        .pop()
        .ok_or(Error::NoBackgroundError(format!(
            "Background image not found: {}",
            { image.title() }
        )));

    tracing::info!("info: {:?}", info);

    // data = site.api_query(
    //     action="query", prop="imageinfo", iiprop="url|size|canonicaltitle",
    //     titles="File:" + filename)
    // res = data["query"]["pages"].values()[0]["imageinfo"][0]
    // name = res["canonicaltitle"][len("File:"):].replace(" ", "_")
    // return name, res["url"], res["descriptionurl"], res["width"], res["height"]

    let image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Crepuscular_rays_at_Sunset_near_Waterberg_Plateau.jpg/2560px-Crepuscular_rays_at_Sunset_near_Waterberg_Plateau.jpg";
    let source_url = "https://commons.wikimedia.org/wiki/File:Crepuscular_rays_at_Sunset_near_Waterberg_Plateau.jpg";
    Ok(Background {
        image_url: String::from(image_url),
        source_url: String::from(source_url),
    })
}

pub async fn get_background() -> Result<Background> {
    let site = Site::new("wikimedia", "commons");
    let bot = site.bot().await.unwrap();

    let images = get_potd_images(&bot).await?;
    let image = images.choose(&mut rand::thread_rng());
    let image =
        image.ok_or_else(|| Error::BackgroundError(String::from("no POTD images found")))?;

    tracing::info!("Background image: {:?}", image.title());
    get_background_from_page(&bot, image).await
}
