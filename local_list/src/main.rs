
use std::fs::File;
use std::io::prelude::*;
use walkdir::{DirEntry, WalkDir};
use sha2::digest::Digest;

fn process<D: Digest + Default, R: Read>(reader: &mut R) -> Result<String, std::io::Error> {
    const BUFFER_SIZE: usize = 1024*1024;
    
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

#[derive(serde::Serialize, Debug)]
struct FileInfo {
    path: String,
    sha1: String,
    sha256: String,
}

#[derive(serde::Serialize, Debug)]
struct ErrInfo {
    path: Option<String>,
    err: String,
}

#[derive(serde::Serialize, Debug)]
#[serde(untagged)]
enum Info {
    Hash(FileInfo),
    Err(ErrInfo),
}

fn process_entry(entry: walkdir::Result<DirEntry>) -> anyhow::Result<Option<Info>> {
    let entry = entry?;
    
    if !entry.file_type().is_file() {
        return Ok(None);
    }
    
    let path = entry.path();
    
    let path_str = match path.to_str() {
        Some(s) => s,
        None => {
            // panic!("non unicode path {:?}", path.display());
            return Err(anyhow::anyhow!("non unicode path {:?}", path.display()))
        },
    };
    
    let mut file = File::open(path)?;
    let hash_sha256 = process::<sha2::Sha256, File>(&mut file)?;
    file.rewind()?;
    let hash_sha1 = process::<sha1::Sha1, File>(&mut file)?;
    let info = Info::Hash(FileInfo {
        path: path_str.to_string(),
        sha1: hash_sha1,
        sha256: hash_sha256,
    });
    
    Ok(Some(info))
}

fn main() {
    let verbose: bool = std::env::var("verbose").map(|x| !x.is_empty()).unwrap_or(false);
    
    let walker = WalkDir::new(".").sort_by_file_name().into_iter();
    
    let mut res: Vec<Info> = Vec::new();
    
    let mut err_count = 0;
    for (i, entry) in walker.into_iter().enumerate() {
        if i % 1000 == 0 || verbose {
            eprintln!("n {} errors {}", i, err_count);
        }
        if verbose {
            eprintln!("{:?}", entry);
        }
        match process_entry(entry) {
            Ok(Some(info)) => {
                if verbose {
                    eprintln!("  {:?}", info);
                }
                res.push(info);
            }
            Ok(None) => (),
            Err(err) => {
                err_count += 1;
                eprintln!("err {:?}", err);
                let path: Option<String> = if let Some(err) = err.downcast_ref::<walkdir::Error>() {
                    err.path().and_then(|x| x.to_str()).map(|x| x.to_string())
                } else if let Some(_err) = err.downcast_ref::<std::io::Error>() {
                    None
                } else {
                    None
                };
                let info = Info::Err(ErrInfo {
                    path: path,
                    err: format!("{:?}", err),
                });
                res.push(info);
                continue
            }
        }
    }
    eprintln!("\nerrors {}", err_count);
    
    let file = File::create("./file_list.json").unwrap();
    serde_json::to_writer_pretty(&file, &res).unwrap();
}
