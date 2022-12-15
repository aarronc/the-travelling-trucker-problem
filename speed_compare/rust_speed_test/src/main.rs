use cgmath::MetricSpace;
use itertools::Itertools;
use rand::seq::SliceRandom;
use rand::Rng;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::collections::VecDeque;
use std::env;
use std::f32::consts::E;
use std::time::Instant;
use thousands::Separable;

// This is my first ever Rust program, so I'm definitely not writing good idiomatic Rust
const DEFAULT_SIMULATION_COUNT: u32 = 500;

fn help() {
    println!(
        "usage:
        ttp_simulation [simulation count]
  Solve the travelling trucker problem with the specified number of simulations, or a default of {}",
        DEFAULT_SIMULATION_COUNT
    );
}

fn main() {
    let start = Instant::now();

    let mut simulation_run_count = 2000;
    let mut seed_route: Vec<usize> = Vec::new();

    // Get some args
    let args: Vec<String> = env::args().collect();
    println!("args.len={}", args.len());
    match args.len() {
        // no arguments passed
        1 => {
            println!(
                "Running with default simulation count of {}",
                DEFAULT_SIMULATION_COUNT
            );
            simulation_run_count = DEFAULT_SIMULATION_COUNT;
        }
        2 => {
            let simulation_run_count_arg = &args[1];
            // parse the number
            let number: u32 = match simulation_run_count_arg.parse() {
                Ok(n) => n,
                Err(_) => {
                    eprintln!(
                        "error: you must give the program a simulation count as the first argument"
                    );
                    return;
                }
            };
            simulation_run_count = number;
            println!("Running with simulation count of {}", simulation_run_count);
        }
        3 => {
            let simulation_run_count_arg = &args[1];
            // parse the number
            let number: u32 = match simulation_run_count_arg.parse() {
                Ok(n) => n,
                Err(_) => {
                    eprintln!(
                        "error: you must give the program a simulation count as the first argument"
                    );
                    return;
                }
            };
            simulation_run_count = number;

            let user_route_arg = &args[2];
            println!("user_route_arg={}", user_route_arg);
            let user_route: Vec<usize> = user_route_arg
                .split(",")
                .into_iter()
                .map(|idx| idx.trim().parse::<usize>().unwrap())
                .collect();
            seed_route = user_route.clone();

            println!("Parsed user route");
        }
        _ => {
            // show a help message
            help();
        }
    }

    let json_string = get_json();

    type Dictionary = HashMap<usize, StarSystem>;
    let star_systems: Dictionary = serde_json::from_str(json_string).unwrap();

    let star_system_keys: Vec<usize> = star_systems
        .keys()
        .sorted()
        .into_iter()
        .map(|x| *x)
        .collect();

    // Dump each system in order, to validate
    for key in star_systems.keys().sorted() {
        println!("Index: {}, star system: {:?}", key, star_systems[key]);
    }

    let star_system_names: HashMap<_, _> = star_systems
        .keys()
        .into_iter()
        .map(|sskey| (sskey, star_systems[sskey].name.clone()))
        .collect();

    let star_system_count = star_systems.keys().len();
    println!("Total system count: {}", star_system_count);

    // validate the user route
    let mut star_system_keys_validation_copy = star_system_keys.clone();
    let mut seed_route_keys_validation_copy = seed_route.clone();
    let seed_route_is_valid = eq_lists_inplace(
        &mut star_system_keys_validation_copy,
        &mut seed_route_keys_validation_copy,
    );

    if seed_route_is_valid {
        println!("Provided route {:?} is valid", seed_route);
    } else if seed_route.len() > 0 {
        println!("Provided route {:?} is NOT valid", seed_route);
        return;
    }

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

        star_system_distances_2d[*source_key as usize][*dest_key as usize] = distance;
        star_system_distances_2d[*dest_key as usize][*source_key as usize] = distance;
    }

    println!(
        "Constructed distance cache with {} entries",
        star_system_distances_2d.len() * star_system_distances_2d.len()
    );

    // move the best route down from floatmax
    let mut overall_best_route_distance = std::f32::MAX;
    let mut overall_best_route: Vec<usize> = Vec::new();

    let _initial_temperature = 900.0;
    let _cooling_ratio = 0.998;
    let iterations_at_temperature: u32 = 2000;
    let mut total_iterations: u64 = 0;

    let mut rng = rand::thread_rng();
    let simulation_durations_count = 10;
    let mut simulation_durations_in_millis: VecDeque<u32> =
        VecDeque::with_capacity(simulation_durations_count);

    let mut last_simulation_iteration_count = 0;

    let mut randomised_route: Vec<usize> = star_system_keys
        .into_iter()
        .map(|x| usize::try_from(x).unwrap())
        .collect_vec();
    randomised_route.shuffle(&mut rng);

    for i in 1..simulation_run_count {
        // let random_initial_temperature = rng.gen_range(500.0..700.0);
        // let random_cooling_ratio = rng.gen_range(0.996..0.998);

        let sim_start = Instant::now();

        let remaining_time = if i as usize > simulation_durations_count {
            let average_sim_duration = simulation_durations_in_millis.iter().sum::<u32>() as f64
                / simulation_durations_count as f64;
            let remaining_simulations = simulation_run_count - i;
            let remaining_seconds_duration =
                average_sim_duration * remaining_simulations as f64 / 1000.0;

            remaining_seconds_duration
        } else {
            0.0 as f64
        };

        let mut output_string = String::new();
        let string_start = format!(
            "Starting simulation {}/{} -- Best route distance {:.1}ly",
            i, simulation_run_count, overall_best_route_distance
        );
        output_string.push_str(&string_start);

        if remaining_time > 0.0 {
            let string_end = format!(
                " -- Estimated time remaining {:.0}s -- Iterations per sim {}",
                remaining_time, last_simulation_iteration_count
            );
            output_string.push_str(&string_end);
        }
        println!("{}", output_string);

        let initital_route: Vec<usize> = if seed_route_is_valid {
            seed_route.clone()
        } else {
            randomised_route.clone()
        };

        let (simulation_best_route, iterations) = run_simulation(
            &initital_route,
            &star_system_distances_2d,
            _initial_temperature,
            iterations_at_temperature,
            _cooling_ratio,
        );

        last_simulation_iteration_count = iterations;

        let simulation_best_route_distance =
            route_distance_2d_array(&simulation_best_route, &star_system_distances_2d);

        if simulation_best_route_distance < overall_best_route_distance {
            overall_best_route_distance = simulation_best_route_distance;
            overall_best_route = simulation_best_route.clone();

            println!(
                "New shortest route found with total distance of {:.1} via indices {:?}",
                overall_best_route_distance, overall_best_route
            );
        }

        // keep a fixed count of the times we average speed from
        if simulation_durations_in_millis.len() == simulation_durations_count {
            simulation_durations_in_millis.pop_front();
        }

        let sim_duration = sim_start.elapsed();
        simulation_durations_in_millis.push_back(sim_duration.subsec_millis());

        total_iterations += iterations as u64;
    }

    let duration = start.elapsed();

    print_named_route(&overall_best_route, &star_system_names);
    println!(
        "Shortest route found with total distance of {:.1} via indices {:?}",
        overall_best_route_distance, overall_best_route
    );
    println!(
        "Completed {} iterations in {} simulations that took {:.1}s ({} iter/sec)",
        total_iterations.separate_with_commas(),
        simulation_run_count,
        duration.as_secs(),
        ((simulation_run_count as f64 * last_simulation_iteration_count as f64
            / duration.as_secs() as f64) as i64)
            .separate_with_commas()
    );
}

fn print_named_route(route: &Vec<usize>, star_systems: &HashMap<&usize, String>) {
    for idx in 1..route.len() {
        let source = route[idx - 1];
        let dest = route[idx];

        println!("{} -> {}", star_systems[&source], star_systems[&dest]);
    }
}

fn run_simulation(
    initial_route: &Vec<usize>,
    distance_cache: &Vec<Vec<f32>>,
    initial_temperature: f32,
    iterations_at_temperature: u32,
    cooling_ratio: f32,
) -> (Vec<usize>, u32) {
    let mut rng = rand::thread_rng();

    let mut best_route: Vec<usize> = Vec::new();
    let mut best_route_distance = f32::MAX;

    let mut current_route = initial_route.clone();

    let mut temperature = initial_temperature;
    let mut loop_count: u32 = 0;

    // For debug output
    // let printed_temperature_band_size = 100.0;
    // let mut last_printed_temperature = temperature;

    // The business end
    while temperature >= 1.0 {
        for _n in 0..iterations_at_temperature {
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

            let new_route_distance = route_distance_2d_array(&new_route, distance_cache);

            let exponent_args = (best_route_distance - new_route_distance) / temperature;
            let accept_probability_f32 = E.powf(exponent_args);

            // let accept_probability = f64::exp(exponent_args.into());
            let random_value: f32 = rng.gen();
            if random_value < accept_probability_f32 {
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

        // Some debug output to monitor
        // if (temperature < (last_printed_temperature - printed_temperature_band_size)) {
        //     println!(
        //         "Global best {:.1} vs current best {:.1} @ temperature: {:0.0} ({} loops)",
        //         overall_best_route_distance, best_route_distance, temperature, loop_count
        //     );
        //     last_printed_temperature = temperature;
        // }

        loop_count += iterations_at_temperature;
        temperature *= cooling_ratio;
    }

    return (best_route, loop_count);
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

fn get_json() -> &'static str {
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

    return json_string;
}

#[derive(Serialize, Deserialize, Debug)]
struct StarSystem {
    name: String,
    x: f32,
    y: f32,
    z: f32,
}

// To compare lists of routes
fn eq_lists_inplace<T>(a: &mut [T], b: &mut [T]) -> bool
where
    T: PartialEq + Ord,
{
    a.sort();
    b.sort();

    a == b
}
