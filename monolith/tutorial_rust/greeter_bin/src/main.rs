fn main() {
    logging_lib::info("Starting...");

    let message = library::greet("Buck2");
    println!("{}", message);

    logging_lib::info("Exit.");
}
