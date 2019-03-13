use std::process::Command;

fn main() {
    // execute from "launcher/" or change path accordingly
    let output = Command::new("sh")
        .arg("-c")
        .arg("python ../main.py")
        .output()
        .expect("Failed to execute script");
    println!("{:?}", output);
}
