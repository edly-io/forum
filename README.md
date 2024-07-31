# Forum App Installation Guide for Tutor Environment

## Description

The Edly Forum app is designed to replace the [CS Comments Service](https://github.com/openedx/cs_comments_service), providing a more robust and flexible forum solution for Open edX instances. This new forum is built in Python and uses MySQL, which enhances performance and maintainability compared to the previous Ruby and MongoDB implementation. The motivation for this rewrite stems from a need for a more streamlined and integrated discussion platform within Open edX, as outlined in the [Axim Funded Contribution Proposal](https://discuss.openedx.org/t/axim-funded-contribution-proposal-forum-rewrite-from-ruby-mongodb-to-python-mysql/12788).

## Prerequisites

Before you begin, ensure you have the following installed:

- A working Open edX instance using the Tutor platform.

## Installation Steps

Follow the steps below to install the Forum app in your Tutor environment:

### 1. Add a Forum App to the openedX dependencies

Open your Tutor configuration file, typically located at `~/.tutor/config.yml`. Add the following package in the `OPENEDX_EXTRA_PIP_REQUIREMENTS`. You can also access the config file via `vim "$(tutor config printroot)/config.yml"` . We are installing the package from Git because the package isn’t yet available on PyPi.

```bash
OPENEDX_EXTRA_PIP_REQUIREMENTS = [
	"git+https://github.com/edly-io/forum.git@master",
]
```

### 2. Save config and rebuild open-edX Image

```yaml
tutor config save
tutor images build openedx
```

### 3. Run Launch

Run the launch based on the environment that you are using. The launch is necessary to build the migrations present in the Forum app. 

```bash
# Dev
tutor dev launch

# Local
tutor local launch

# K8S
tutor k8s launch
```

### 4. Accessing the Forum

There are no changes needed in the [Discussion MFE](https://github.com/openedx/frontend-app-discussions). You should see the forum interface where users can start discussions, post comments, and interact with each other. In the backend, the API calls are made via the Forum app instead of the CS Comments Service.

### 5. Development (For Developers)

In certain scenarios, you may need to mount the Forum package for extending or debugging features. Follow these steps to accomplish this:

1. **Create the Plugin File:**
Create a file named `forumv2.py` inside the `tutor-plugins` folder. You can navigate to this folder using the command: `$(tutor plugins printroot)`.
2. **Insert the Following Code:**
Paste the following code into `forumv2.py`. Tutor consider this file as a plugin and you can verify it via `tutor plugins list` command. 
    
    ```python
    from tutor import hooks
    
    hooks.Filters.MOUNTED_DIRECTORIES.add_item(("openedx", "forum"))
    
    ```
    
3. **Enable the Plugin:**
Enable the newly created plugin with the following command:
    
    ```bash
    tutor plugins enable forumv2
    ```
    
4. **Clone and mount the package**
    
    ```bash
    git clone https://github.com/edly-io/forum.git
    tutor mounts add <forum directory>
    ```
    

## License

This project is licensed under the MIT License.
