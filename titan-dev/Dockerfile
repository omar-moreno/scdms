# Use Ubuntu 24.04 as the base image
FROM ubuntu:24.04
  
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install Apache
RUN apt-get update && \
    apt-get install -y apache2 \
		       libapache2-mod-php \
                       php \
		       php-cli \
                       php-fpm \
                       php-mysql \
                       php-json \
                       php-opcache \
                       php-gd \
                       php-curl \
                       php-mbstring \
                       php-xml \
		       perl \
		       libapache2-mod-perl2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Enable Apache modules for CGI and Perl
RUN a2enmod php8.3 && \
    a2enmod cgi && \
    a2enmod perl

# Create a basic Perl CGI script for testing
RUN mkdir -p /usr/lib/cgi-bin && \
    echo '#!/usr/bin/perl\nprint "Content-type: text/html\\n\\nHello from Perl CGI!"' > /usr/lib/cgi-bin/hello.pl && \
    chmod +x /usr/lib/cgi-bin/hello.pl

# Create a sample PHP file
RUN echo '<?php echo "Hello from PHP!"; ?>' > /var/www/html/index.php

# Set PHP file as default landing page
RUN sed -i 's/DirectoryIndex .*/DirectoryIndex index.php index.html/' /etc/apache2/mods-enabled/dir.conf

# Expose port 80 for HTTP
EXPOSE 80
 
# Enable Apache to run in the foreground
CMD ["apachectl", "-D", "FOREGROUND"]
