# GFS-STILT Model

An automated backward trajectory dispersion platform based on GFS meteorological data and the STILT model for identifying potential source area. It supports containerized deployment via Docker, scheduled tasks via Django + Celery, and provides APIs for retrieving simulation results.

- 📘 [Learn more about STILT](https://uataq.github.io/stilt/#/install)  
- 🌍 

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourname/gfs-stilt-service.git
cd gfs-stilt-service
```
### 2. Build the Docker image
```
docker build -t gfs-stilt-model .
```
### 3. Run the container
```
  docker run -d --name gfs-stilt-model -p 8000:8000 -p 5555:5555 \
  -v $(pwd)/arlout:/usr/local/stilt/arlout \
  -v $(pwd)/stiltout_data:/usr/local/stilt/stiltout_data \
  gfs-stilt-model 

```

## GFS Meteorological Data

The system uses GFS 0.25-degree resolution forecast data. You can manually browse and download GFS files here:

https://www.ready.noaa.gov/data/archives/gfs0p25(https://www.ready.noaa.gov/data/archives/gfs0p25)

> Note: Historical and forecast data can also be downloaded automatically via script.


## STILT Executable Registration

In order to run STILT with forecast meteorology, you must obtain the official HYSPLIT binary.

Apply for access here:

https://www.ready.noaa.gov/HYSPLIT_register.php(https://www.ready.noaa.gov/HYSPLIT_register.php)

After registering, download the executables, unzip them, and copy to:
```
build/bin/linux-gnu/
```
Or place them directly into the Docker image under ${STILT_WD}/exe/.
