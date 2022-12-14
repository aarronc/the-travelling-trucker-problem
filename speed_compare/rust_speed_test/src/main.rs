use cgmath::num_traits::ToPrimitive;
use cgmath::MetricSpace;
use itertools::Itertools;
use permutator::{Combination, XPermutationIterator};
use rand::rngs::ThreadRng;
use rand::seq::SliceRandom;
use rand::Rng;
use rayon::prelude::*; // for multi-core?
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
// 0.6.5
use std::time::Instant;
use thousands::Separable;

// This is my first ever Rust program, so I'm definitely not writing good idiomatic Rust

struct Candidate {
    route: Vec<usize>,
}

fn main() {
    let start = Instant::now();

    println!("Hello, world!");

    let best_route = [
        12, 15, 28, 5, 25, 21, 22, 29, 26, 0, 27, 17, 31, 30, 20, 19, 16, 14, 8, 9, 4, 2, 23, 6,
        24, 32, 3, 7, 13, 11, 1, 10, 18,
    ];

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

    let star_system_count = star_systems.keys().len();
    println!("Total system count: {}", star_system_count);

    // 2d array of cached distances
    let mut star_system_distances_2d: Vec<Vec<f32>> =
        vec![vec![0.0; star_system_count]; star_system_count];

    for (source_key, dest_key) in star_system_keys.iter().tuple_combinations() {
        let sss = &star_systems[source_key];
        let dss = &star_systems[dest_key];

        // This is the only place we use cgmath, so it can be easily refactored out if required
        let source_pos = cgmath::vec3(sss.x, sss.y, sss.z);
        let dest_pos = cgmath::vec3(dss.x, dss.y, dss.z);
        let distance = source_pos.distance(dest_pos);

        star_system_distances_2d[**source_key as usize][**dest_key as usize] = distance;
        star_system_distances_2d[**dest_key as usize][**source_key as usize] = distance;
    }

    println!(
        "Constructed distance cache with {} entries",
        star_system_distances_2d.len() * star_system_distances_2d.len()
    );

    // for (key, value) in star_systems.into_iter() {
    //     println!("Index: {}, star system: {:?}", key, value);
    // }

    println!(
        "Best route from JS: {}",
        route_distance_2d_array(&best_route, &star_system_distances_2d)
    );

    // move the best route down from floatmax
    let mut best_route_distance = std::f32::MAX;
    let mut best_route: Vec<usize> = Vec::new();

    // We need to deref the keys in this map with * as we originally got pointers from the original parsed JSON
    let mut current_route: Vec<usize> = star_system_keys
        .into_iter()
        .map(|x| usize::try_from(*x).unwrap())
        .collect_vec();

    // Permutation system
    // let mut perm_iter = XPermutationIterator::new(&mutable_system_indices, |_| true);

    // Initialise an RNG for the shuffles
    let mut rng = rand::thread_rng();

    // shuffle once, to allow us to re-run the binary with a randomised outcome each time
    current_route.shuffle(&mut rng);

    let mut same_count = 0;

    let cooling_ratio = 0.998;
    let mut temperature = 700.0;
    let mut loop_count = 0;
    let iterations_at_temperature = 2000;

    let printed_temperature_band_size = 20.0;

    let mut last_printed_temperature = temperature;

    // The business end
    while temperature >= 1.0 {
        for n in 0..iterations_at_temperature {
            // Pick a random pair of indices, start lower than end
            let start = rng.gen::<usize>() % current_route.len();
            let end = rng.gen::<usize>() % current_route.len();
            let (start, end) = if start < end {
                (start, end)
            } else {
                (end, start)
            };

            // println!("Swapping {} and {}", start, end);

            // Make a trivial pair swap for the first route variant
            let mut new_route = current_route.clone();
            new_route.swap(start, end);

            let new_route_distance = route_distance_2d_array(&new_route, &star_system_distances_2d);

            let args = ((best_route_distance - new_route_distance) / temperature);
            let accept_probability = f64::exp(args.into());
            let random_value: f64 = rng.gen();
            if (random_value < accept_probability) {
                // println!(
                //     "New best route dist {} vs {} was from swapped indices {} and {}: {:?}",
                //     shortest_route, best_route_distance, start, end, star_system_indices_swapped
                // );
                current_route = new_route.clone();
            }

            if new_route_distance < best_route_distance {
                best_route_distance = new_route_distance;
                best_route = new_route.clone();
            }
        }

        if (temperature < (last_printed_temperature - printed_temperature_band_size)) {
            println!(
                "Temperature: {:.0} ({} loops) - Current best route distance {:.1}",
                temperature, loop_count, best_route_distance
            );
            last_printed_temperature = temperature;
        }

        loop_count += iterations_at_temperature;
        temperature *= cooling_ratio;
    }

    let duration = start.elapsed();
    // println!("Best route:");
    // for idx in 1..best_route.len() {
    //     let source = best_route[idx - 1] as u32;
    //     let dest = best_route[idx] as u32;

    //     println!(
    //         "{} -> {}",
    //         star_systems[&source].name, star_systems[&dest].name
    //     );
    // }

    println!(
        "Shortest route found with total distance of {} via indices {:?}",
        best_route_distance, best_route
    );
    println!(
        "completed {} iterations in {:?} ({:?}/iter)",
        loop_count.separate_with_commas(),
        duration,
        duration / loop_count as u32
    );
}

fn route_distance_2d_array(input: &[usize], distance_cache: &Vec<Vec<f32>>) -> f32 {
    let mut total_distance = 0.0;
    let route_visit_count = input.len();

    for idx in 1..route_visit_count {
        let source = input[idx - 1];
        let dest = input[idx];
        let distance: f32 = distance_cache[source][dest];
        // println!("{} -> {} = {}", source, dest, distance);
        total_distance += distance;
    }

    return total_distance;
}

// Hacked up a different method to take a vec rather than an array
fn route_distance_vec_2d_array(input: &Vec<&u32>, distance_cache: &Vec<Vec<f32>>) -> f32 {
    let mut total_distance = 0.0;
    let route_visit_count = input.len();

    for idx in 1..route_visit_count {
        let source = *input[idx - 1] as usize;
        let dest = *input[idx] as usize;
        let distance: f32 = distance_cache[source][dest];
        // println!("{} -> {} = {}", source, dest, distance);
        total_distance += distance;
    }

    return total_distance;
}

fn get_route_distance(distance_matrix: &[Vec<f64>], route: &[usize]) -> f64 {
    let mut route_iter = route.iter();
    let mut current_city = match route_iter.next() {
        None => return 0.0,
        Some(v) => *v,
    };

    route_iter.fold(0.0, |mut total_distance, &next_city| {
        total_distance += distance_matrix[current_city as usize][next_city as usize];
        current_city = next_city;
        total_distance
    })
}

fn get_distance_matrix(star_systems: &[(f64, f64)]) -> Vec<Vec<f64>> {
    star_systems
        .iter()
        .map(|row| {
            star_systems
                .iter()
                .map(|column| ((column.0 - row.0).powi(2) + (column.1 - row.1).powi(2)).sqrt())
                .collect::<Vec<f64>>()
        })
        .collect::<Vec<Vec<f64>>>()
}

#[derive(Serialize, Deserialize, Debug)]
struct StarSystem {
    name: String,
    x: f32,
    y: f32,
    z: f32,
}
