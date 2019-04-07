use std::process::Command;

/// Launcher for TUInvetory
fn main() {
    
    // execute from "launcher/" or change path accordingly
    let output = if cfg!(target_os = "windows") {
        Command::new("cmd")
            .args(&["/C"]) // "/Q" hides terminal but also prevents Qt-GUI from showing
            .arg("python ../main.py")
            .output()
            .expect("Failed to execute process");
    } else {
        Command::new("sh")
            .arg("-c")
            .arg("python ../main.py")
            .output()
            .expect("Failed to execute process");
    };
    println!("{:?}", output);
}
