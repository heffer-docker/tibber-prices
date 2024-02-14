# Tibber Price Diagram

This docker container creates a simple bar diagram with the hourly Tibber prices for today and tomorrow based on the given Tibber API key.

## Usage

```
docker pull ghcr.io/heffer-docker/tibber-prices:main
docker run --rm -u $(id -u):$(id -g) -v $(pwd)/output:/output -e TIBBER_API_KEY=<insert your Tibber API token> ghcr.io/heffer-docker/tibber-prices:main
```

After the container has finished there will be up to two PNG files created (depending if the prices for tomorrow are available) inside the mapped `output` directory.
