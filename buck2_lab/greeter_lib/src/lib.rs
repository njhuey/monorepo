pub fn greet(name: &str) -> String {
    logging_lib::info("Entered greet function in library");

    let greeting = format!("Hello, {}!", name);

    logging_lib::info("Exiting greet function in library");
    greeting
}
