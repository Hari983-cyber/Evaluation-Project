import subprocess
import os
import sys

def check_docker_compose_installed():
    if not os.path.exists("/usr/bin/docker-compose"):
        print("Docker Compose is not installed.")
        print("Please install Docker Compose first.")
        sys.exit(1)

if __name__ == "__main__":
    check_docker_compose_installed()

    if len(sys.argv) != 2:
        print("Usage: python create_wordpress_site.py <site_name>")
        sys.exit(1)

    site_name = sys.argv[1]

    # Create a docker-compose file.
    docker_compose_file_path = os.path.join(os.getcwd(), "docker-compose.yml")
    with open(docker_compose_file_path, "w") as f:
        f.write("""
version: '3.3'

services:
  wordpress:
    image: wordpress:latest
    volumes:
      - ./wordpress:/var/www/html
    ports:
      - 80:80
    depends_on:
      - nginx

  nginx:
    image: nginx:latest
    ports:
      - 8080:80
    volumes:
      - ./wordpress:/var/www/html
      - /path/to/nginx/config:/etc/nginx

volumes:
  mysqldata:
""")

    # Check if the site name is valid.
    if not site_name.startswith("http://") and not site_name.startswith("https://"):
        site_name = "http://" + site_name

    # Create a /etc/hosts entry for the site.
    hostname = site_name.split("/")[1]
    with open("/etc/hosts", "a") as f:
        f.write("http://localhost {hostname}\n")

    # Change the permissions on the docker-compose.yml file so that it is owned by the user `hari`.
    subprocess.call(["sudo", "chown", "-R", "hari", "docker-compose.yml"])

    # Start the Docker containers.
    subprocess.call(["docker-compose", "up", "-d"])

    # Open the site in a browser.
    subprocess.call(["xdg-open", site_name])
