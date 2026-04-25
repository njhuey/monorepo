#[cfg(test)]
mod tests {
    use library;

    #[test]
    fn test_greet() {
        assert_eq!(library::greet("World"), "Hello, World!");
        assert_eq!(library::greet("Buck2"), "Hello, Buck2!");
    }

    #[test]
    fn test_greet_empty() {
        assert_eq!(library::greet(""), "Hello, !");
    }
}
