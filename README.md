

# Travelling Trucker Problem (TTP)

## What is this project?
For a long time, we have been trying to find out the fastest route between all of the systems that the Hutton Orbital Truckers own. This is an attempt using two main approaches to find the shortest distance in Lightyears in total from all 33 systems the Truckers owned at the time this attempt was started. 

## Versions
3 versions of this program cover the 2 approaches to this problem.
- Python Versions that work on the principle of brute-force (CPU and GPU) version
- Rust Version that works on the simulated annealing principal 

## Python 3.10 CPU version
worker.py uses the CPU and requires the following modules
- Backoff (`pip install backoff`)
- Requests (`pip install requests`)
- Zlib (`pip install zlib`)

You can use the standard python 3 to run this but we have found the most performance increase using pypy3, this can make the program 10x faster.

**TIP -> You can run a copy for each physical CPU without much performance impact**

## Python 3.10 GPU Version
gpu_worker.py  has more requirements :
- CuDA 11.7 toolkit (`cuda_11.7.0_516.01_windows.exe`)
- CuPY 11x (`pip install cupy-cuda11x`)
- Numba (`pip install numba`)
- Numpy (`pip install numpy`)
- Backoff (`pip install backoff`)
- Requests (`pip install requests`)

As part of the Cuda Toolkit installation process, you may have to download additional dependencies, there is a good CUDA toolkit installation guide that will take you through the whole process.

**Tip -> This Will only ever use 1 GPU, your Promary GPU (the one that is seen as GPU 0)**

## Rust (Simulated annealing)
This takes a different approach and uses simulated annealing to find the best route.
find the project in the `\speed_compare\rust_speed_test\` folder and then use the `cargo run` command.

## Coming Soon
We have a few things coming soon in regard to this project:
- Commander leaderboards 
- Team leaderboards
- Lowest Distance that is currently found with the associated route.

**and more cool things as we think of them**
