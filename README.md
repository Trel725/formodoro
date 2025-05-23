# Formodoro: a ridiculously simple form data storage 

## Problem

Even a simple static webpage frequently ends up with having a need to store some form data. Think of simple "business card" type of website, where you have a contact form. The standard solution is to use some third party service like Google Forms, but that is not always the best solution, especially when valuing privacy. After all, there is no escape from using some kind of backend if you don't want to send your data to some third party service. 

## Solution

Formodoro is a simple local solution to this problem. It is an extremely simple form data storage that proxies both form data and JSON data to MongoDB. Think of it as of a little better version of long JSON with your form data. It is up to you how to use this data later, you can bundled Mongo Express to export it to convenient format.  

In addition, Formodoro includes nice [notifiers library](https://github.com/liiight/notifiers) to send notifications to your favorite service. Refer to the notifiers documentation for a list of supported notification services.

## Features

- Extremely simple to use
- Select MongoDB or TinyDB as a backend
- Saves arbitrary form and JSON data to the selected backend
- Supports CORS for easy integration with static websites
- Supports multiple notification services
- Optionally redirects to a custom URL after form submission for totally static websites

## Installation and Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/Trel725/formodoro.git
   cd formodoro
   ```
2. Adjust environment variables in docker-compose.yml. See its content for details. In the simplest case, you can only change `CORS_ORIGINS` to your website URL. It is a good idea to also set up notification by setting `NOTIFIERS_PROVIDER` and its settings, as well as change passwords. The most important is `ME_CONFIG_BASICAUTH_USERNAME` as it's exposed externally.
3. Run the application:
   ```bash
   docker-compose up -d
   ```
   the app is available at port 28100 by default.
4. Open your browser and go to `http://localhost:8081` to see the Mongo Express interface.
5. To test the form submission, you can use the following curl command:
   ```bash
    curl -H "Origin: http://localhost:8080" -X POST http://localhost:28100/submit -d 'name=John' -d 'email=john@example.com' -d 'message=Hello'
    ```
6. Or you can use the following curl command to send JSON data:
   ```bash
   curl -H "Origin: http://localhost:8080" -X POST http://localhost:28100/submit -H "Content-Type: application/json" -d '{"name": "John", "email": "john@example.com", "message": "Hello"}'
   ```

Additionally, you can pass the redirect URL as a query parameter, e.g.
`http://localhost:28100/submit?redirect=http://example.com`.
This might be useful if you want to redirect to a different URL after form submission.

## MongoDB vs TinyDB

Formodoro supports two backends: MongoDB and TinyDB. MongoDB is a powerful NoSQL database that is suitable for production use, while TinyDB is a lightweight, file-based database that is easy to set up and use for small projects or testing purposes. TinyDB is true open source, while MongoDB has its own license, enforcing some restrictions on usage, see [MongoDB license](https://www.mongodb.com/licensing/server-side-public-license). To be completely open source, Formodoro uses TinyDB as a backend by default. If you want to use MongoDB, you need to use `docker-compose.mongo.yml` override as follows:
```bash
docker-compose -f docker-compose.yml -f docker-compose.mongo.yml up -d
```

## Example

In the simplest case, you can just add URL of your server running Formodoro to your form action. For example, if your server is running on `https://yourserver.com`, you can use the following HTML code:
```
<form
    action="https://yourserver.com/submit/?redirect=https://yourserver.com/success"
    method="POST"
>
    <label for="name">Name:</label>
    <input type="text" id="name" name="name" required />

    <label for="surname">Surname:</label>
    <input type="text" id="surname" name="surname" required />

    <button type="submit">Submit</button>
</form>
``` 

Note that the `redirect` parameter can be used to redirect to a different URL after form submission, e.g. to a success page without any JS or other dependencies. If the method fails, redirect will not be performed.

Take into account that this example assumes that `/submit` is mapped to the Formodoro server. If you are using NGINX server, this can be achieved by adding the following lines to your NGINX configuration:
```
    location /submit/ {
       proxy_pass http://localhost:28100/submit;
        proxy_set_header Host $host;
        proxy_set_header Origin $http_origin;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

```
When reverse proxy is not used, you can directly use the Formodoro server URL in the form action, e.g. `http://yourserver.com:28100/submit`, but this is strongly discouraged as it uses naked HTTP.


## Other

Ideas for improvement are warmly welcomed. 