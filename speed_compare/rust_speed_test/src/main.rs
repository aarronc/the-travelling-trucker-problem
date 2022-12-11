use cgmath::MetricSpace;
use itertools::Itertools;
use rand::seq::SliceRandom;
use rayon::prelude::*; // for multi-core
use serde::{Deserialize, Serialize};
use std::collections::HashMap; // 0.6.5
use std::time::Instant;
use thousands::Separable;

fn main() {
    let start = Instant::now();

    println!("Hello, world!");

    let json_string = r#"
    {
        "0":{
          "name":"van Maanen's Star",
          "x":-6.3125,
          "y":-11.6875,
          "z":-4.125
        },
        "1":{
          "name":"Wolf 124",
          "x":-7.25,
          "y":-27.1562,
          "z":-19.0938
        },
        "2":{
          "name":"Midgcut",
          "x":-14.625,
          "y":10.3438,
          "z":13.1562
        },
        "3":{
          "name":"PSPF-LF 2",
          "x":-4.40625,
          "y":-17.1562,
          "z":-15.3438
        },
        "4":{
          "name":"Wolf 629",
          "x":-4.0625,
          "y":7.6875,
          "z":20.0938
        },
        "5":{
          "name":"LHS 3531",
          "x":1.4375,
          "y":-11.1875,
          "z":16.7812
        },
        "6":{
          "name":"Stein 2051",
          "x":-9.46875,
          "y":2.4375,
          "z":-15.375
        },
        "7":{
          "name":"Wolf 25",
          "x":-11.0625,
          "y":-20.4688,
          "z":-7.125
        },
        "8":{
          "name":"Wolf 1481",
          "x":5.1875,
          "y":13.375,
          "z":13.5625
        },
        "9":{
          "name":"Wolf 562",
          "x":1.46875,
          "y":12.8438,
          "z":15.5625
        },
        "10":{
          "name":"LP 532-81",
          "x":-1.5625,
          "y":-27.375,
          "z":-32.3125
        },
        "11":{
          "name":"LP 525-39",
          "x":-19.7188,
          "y":-31.125,
          "z":-9.09375
        },
        "12":{
          "name":"LP 804-27",
          "x":3.3125,
          "y":17.8438,
          "z":43.2812
        },
        "13":{
          "name":"Ross 671",
          "x":-17.5312,
          "y":-13.8438,
          "z":0.625
        },
        "14":{
          "name":"LHS 340",
          "x":20.4688,
          "y":8.25,
          "z":12.5
        },
        "15":{
          "name":"Haghole",
          "x":-5.875,
          "y":0.90625,
          "z":23.8438
        },
        "16":{
          "name":"Trepin",
          "x":26.375,
          "y":10.5625,
          "z":9.78125
        },
        "17":{
          "name":"Kokary",
          "x":3.5,
          "y":-10.3125,
          "z":-11.4375
        },
        "18":{
          "name":"Akkadia",
          "x":-1.75,
          "y":-33.9062,
          "z":-32.9688
        },
        "19":{
          "name":"Hill Pa Hsi",
          "x":29.4688,
          "y":-1.6875,
          "z":25.375
        },
        "20":{
          "name":"Luyten 145-141",
          "x":13.4375,
          "y":-0.8125,
          "z":6.65625
        },
        "21":{
          "name":"WISE 0855-0714",
          "x":6.53125,
          "y":-2.15625,
          "z":2.03125
        },
        "22":{
          "name":"Alpha Centauri",
          "x":3.03125,
          "y":-0.09375,
          "z":3.15625
        },
        "23":{
          "name":"LHS 450",
          "x":-12.4062,
          "y":7.8125,
          "z":-1.875
        },
        "24":{
          "name":"LP 245-10",
          "x":-18.9688,
          "y":-13.875,
          "z":-24.2812
        },
        "25":{
          "name":"Epsilon Indi",
          "x":3.125,
          "y":-8.875,
          "z":7.125
        },
        "26":{
          "name":"Barnard's Star",
          "x":-3.03125,
          "y":1.375,
          "z":4.9375
        },
        "27":{
          "name":"Epsilon Eridani",
          "x":1.9375,
          "y":-7.75,
          "z":-6.84375
        },
        "28":{
          "name":"Narenses",
          "x":-1.15625,
          "y":-11.0312,
          "z":21.875
        },
        "29":{
          "name":"Wolf 359",
          "x":3.875,
          "y":6.46875,
          "z":-1.90625
        },
        "30":{
          "name":"LAWD 26",
          "x":20.9062,
          "y":-7.5,
          "z":3.75
        },
        "31":{
          "name":"Avik",
          "x":13.9688,
          "y":-4.59375,
          "z":-6.0
        },
        "32":{
          "name":"George Pantazis",
          "x":-12.0938,
          "y":-16.0,
          "z":-14.2188
        }
      }
    "#;

    type Dictionary = HashMap<u32, StarSystem>;
    let star_systems: Dictionary = serde_json::from_str(json_string).unwrap();

    let star_system_keys = Vec::from_iter(star_systems.keys().sorted());

    // Dump each system in order, to validate
    for key in star_systems.keys().sorted() {
        println!("Index: {}, star system: {:?}", key, star_systems[key]);
        // star_system_distances.insert(pair_key, distance);
    }

    println!("Total system count: {}", star_systems.keys().len());

    // We use a u32 for the lookup. This must always be done via shifting the highest
    // route index by 16 and bitwise andind with the lower index
    let mut star_system_distances: HashMap<u32, f32> = HashMap::new();

    for (source_key, dest_key) in star_system_keys.iter().tuple_combinations() {
        let sss = &star_systems[source_key];
        let dss = &star_systems[dest_key];

        // This is the only place we use cgmath, so it can be easily refactored out if required
        let source_pos = cgmath::vec3(sss.x, sss.y, sss.z);
        let dest_pos = cgmath::vec3(dss.x, dss.y, dss.z);
        let distance = source_pos.distance(dest_pos);

        // Fold the source and dest into a single u32 by forcing each to be a 16bit uint
        // which means we can only ever have a max of 65535 systems, which is probably ok
        let source_key_int: u32 = **source_key;
        let dest_key_int: u32 = **dest_key;
        let compound_key = dest_key_int << 16 | source_key_int;

        // Debug checking
        // println!("{} -> {}", source_key_int, dest_key_int);
        // println!("source = {:#034b}", source_key);
        // println!("dest = {:#034b}", dest_key);
        // println!("compound = {:#034b}", compound_key);
        // println!("------");

        // Extract to double check I've got this right
        // let lower_mask: u32 = 65535;
        // let derived_source = compound_key & lower_mask;
        // let derived_dest = (compound_key >> 16) & lower_mask;
        // println!("derived {} -> {}", derived_source, derived_dest);
        // println!("--!!--");

        star_system_distances.insert(compound_key, distance);
    }

    println!(
        "Constructed distance cache with {} entries",
        star_system_distances.keys().len()
    );

    // for (key, value) in star_systems.into_iter() {
    //     println!("Index: {}, star system: {:?}", key, value);
    // }

    // move the best route down from floatmax
    let mut best_route_distance = std::f32::MAX;
    let mut best_route: Vec<u32> = Vec::new();

    // We need to deref the keys in this map with * as we originally got pointers from the original parsed JSON
    let mut mutable_system_indices = star_system_keys.into_iter().map(|x| *x).collect_vec();

    // Initialise an RNG for the shuffles
    let mut rng = rand::thread_rng();

    // Define how many loops we want in total
    let loop_count = 5000000;

    println!("Looping for {}", loop_count.separate_with_commas());

    // The business end
    for route_loop in 1..loop_count {
        // Shuffle to get a random walk
        mutable_system_indices.shuffle(&mut rng);

        // Calculate the total distance via route_distance(), utilising our distance_cache

        let route_dist = route_distance(&mutable_system_indices, &star_system_distances);
        // println!("Checking {} vs existing {}", route_dist, best_route);
        // If it's better, make a note of it
        if route_dist < best_route_distance {
            best_route_distance = route_dist;
            best_route = mutable_system_indices.clone();
        }
    }

    let duration = start.elapsed();
    println!(
        "Shortest route found with total distance of {} via indices {:?}",
        best_route_distance, best_route
    );

    for idx in 1..best_route.len() {
        let source = best_route[idx - 1];
        let dest = best_route[idx];

        println!(
            "{} -> {}",
            star_systems[&source].name, star_systems[&dest].name
        );
    }

    println!(
        "completed {} iterations in {:?} ({:?}/iter)",
        loop_count.separate_with_commas(),
        duration,
        duration / loop_count
    );
}

fn route_distance(input: &[u32], distance_cache: &HashMap<u32, f32>) -> f32 {
    let mut total_distance = 0.0;
    let route_visit_count = input.len();

    for idx in 1..route_visit_count {
        let source = input[idx - 1];
        let dest = input[idx];
        let compound_key = if source > dest {
            source << 16 | dest
        } else {
            dest << 16 | source
        };
        let distance: f32 = distance_cache[&compound_key];
        // println!("{} -> {} = {}", source, dest, distance);
        total_distance += distance;
    }

    return total_distance;
}

#[derive(Serialize, Deserialize, Debug)]
struct StarSystem {
    name: String,
    x: f32,
    y: f32,
    z: f32,
}
