# Forum App Installation Guide for Tutor Environment

## Description

The Edly Forum app is designed to replace the [CS Comments Service](https://github.com/openedx/cs_comments_service), providing a more robust and flexible forum solution for Open edX instances. This new forum is built in Python and uses MySQL, which enhances performance and maintainability compared to the previous Ruby and MongoDB implementation. The motivation for this rewrite stems from a need for a more streamlined and integrated discussion platform within Open edX, as outlined in the [Axim Funded Contribution Proposal](https://discuss.openedx.org/t/axim-funded-contribution-proposal-forum-rewrite-from-ruby-mongodb-to-python-mysql/12788).

## Prerequisites

Before you begin, ensure you have the following installed:

- A working Open edX instance using the Tutor platform.

## Installation Steps

Follow the steps below to install the Forum app in your Tutor environment:

### 1. Add a Forum App to the openedX dependencies

To add this package to the Open edX dependencies, include it in the `OPENEDX_EXTRA_PIP_REQUIREMENTS`. Since the package is not yet available on PyPI, we will install it directly from the Git repository.

Run the following command to append the package to your Tutor configuration:

```bash
tutor config save --append 'OPENEDX_EXTRA_PIP_REQUIREMENTS=git+https://github.com/edly-io/forum.git@master'
```

### 2. Save config and rebuild open-edX Image

```yaml
tutor config save
tutor images build openedx
```

### 3. Run Launch

Run the launch commad. It is necessary for building the migrations present in the Forum app. 

```bash
# Dev
tutor dev launch
```

### 4. Accessing the Forum

There are no changes needed in the [Discussion MFE](https://github.com/openedx/frontend-app-discussions). You should see the forum interface where users can start discussions, post comments, and interact with each other. In the backend, the API calls are made via the Forum app instead of the CS Comments Service.

### 5. Development (For Developers)

In certain scenarios, you may need to mount the Forum package for extending or debugging features. For this, you need to install the [forumv2](https://gist.github.com/taimoor-ahmed-1/9e947a06d127498a328475877e41d7c0) plugin. Follow these steps to accomplish this:

1. **Clone the forum repo:**
    ```bash
    git clone git@github.com:edly-io/forum.git
    ```
2. **Mount the repo:**    
    ```bash
    tutor mounts add path/to/forum/repo
    ```
    
3. **Install this plugin:**    
    ```bash
    tutor plugins install https://gist.githubusercontent.com/taimoor-ahmed-1/9e947a06d127498a328475877e41d7c0/raw/6152bdc312f941e79d50e2043f00d3d059de70a7/forum-v2.py

    ```

4. **Enable the plugin:**
    
    ```bash
    tutor plugins enable forumv2
    ```

5. **Save Changes:**
    
    After the plugin is enabled, further changes to the plugin code are applied with:
    ```bash
    tutor config save
    ```

6. **Build the openedx-dev Docker image:**
    ```bash
    tutor images build openedx-dev
    ```

7. **Launch the platorm:**
    ```bash
    tutor dev launch
    ```

## License

This project is licensed under the MIT License.
