
use std::fs::File;
use std::io::prelude::*;
use walkdir::{DirEntry, WalkDir};
use sha2::digest::Digest;

fn process<D: Digest + Default, R: Read>(reader: &mut R, name: &str) -> Result<String, std::io::Error> {
    const BUFFER_SIZE: usize = 1024;
    
    let mut sh = D::default();
    let mut buffer = [0u8; BUFFER_SIZE];
    loop {
        let n = match reader.read(&mut buffer) {
            Ok(n) => n,
            Err(e) => return Err(e),
        };
        sh.update(&buffer[..n]);
        if n == 0 || n < BUFFER_SIZE {
            break;
        }
    }
    // print_result(&sh.finalize(), name);
    // sh.result_str()
    let output = sh.finalize();
    let slice = output.as_slice();
    // println!("{:x?}", slice);
    let mut out_str = String::new();
    for byte in slice.iter() {
        let b_str = format!("{:0>2x}", byte);
        out_str.push_str(&b_str);
    }
    
    Ok(out_str)
    // Ok("".to_string())
}

#[derive(serde::Serialize)]
struct FileInfo {
    path: String,
    sha1: String,
    sha256: String,
}

fn main() {
    let walker = WalkDir::new(".").into_iter();
    
    let mut res: Vec<FileInfo> = Vec::new();
    
    for entry in walker {
        let entry = entry.unwrap();
        // let metadata = entry.metadata().unwrap();
        if !entry.file_type().is_file() {
            continue
        }
        
        // println!("{:?}", entry);
        let path = entry.path();
        
        let path_str = match path.to_str() {
            Some(s) => s,
            None => {
                panic!("non unicode path {:?}", path.display());
            },
        };
        
        let mut file = File::open(path).unwrap();
        let hash_sha256 = process::<sha2::Sha256, File>(&mut file, "").unwrap();
        file.rewind();
        let hash_sha1 = process::<sha1::Sha1, File>(&mut file, "").unwrap();
        let info = FileInfo {
            path: path_str.to_string(),
            sha1: hash_sha1,
            sha256: hash_sha256,
        };
        res.push(info);
    }
    
    let file = File::create("./file_list.json").unwrap();
    serde_json::to_writer_pretty(&file, &res).unwrap();
}
