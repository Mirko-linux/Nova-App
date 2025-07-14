use warp::{Filter, Rejection, Reply};
use std::path::PathBuf;

async fn upload_file(file: warp::multipart::FormData) -> Result<impl Reply, Rejection> {
    println!("File ricevuto!");
    Ok(warp::reply::json(&{ "status": "success" }))
}

pub async fn start_web_server() {
    let upload_route = warp::path("upload")
        .and(warp::post())
        .and(warp::multipart::form().max_length(10_000_000)) // 10MB
        .and_then(upload_file);

    warp::serve(upload_route)
        .run(([127, 0, 0, 1], 8080))
        .await;
}
