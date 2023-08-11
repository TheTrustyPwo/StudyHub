[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GNU GPLv3 License][license-shield]][license-url]


<!-- PROJECT TITLE -->
<!--suppress HtmlDeprecatedAttribute, HtmlUnknownAnchorTarget -->

<div align="center">
<h3 align="center">Study Hub</h3>
  <p align="center">
    This is the codebase of StudyHub, an innovative educational platform designed to enhance learning and collaboration between students.
    <br/>
    <a href="https://github.com/TheTrustyPwo/StudyHub/issues">Report Bug</a>
    ·
    <a href="https://github.com/TheTrustyPwo/StudyHub/issues">Request Feature</a>
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#local-setup">Local Setup</a></li>
        <li><a href="#testing">Testing</a></li>
        <li><a href="#deployment">Deployment</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->

## About The Project

Introducing StudyHub: 🚀 Your Academic Launchpad!

In a digital era brimming with possibilities, education should be accessible, engaging, and collaborative. But we know the struggle: reliable academic support can be elusive, leaving growth opportunities untapped. That's why StudyHub emerged, combining the pulse of social media with the finesse of advanced AI tools.

🔮 With AI as its superpower, StudyHub becomes your academic ally. It's not just a platform; it's your bridge to smarter learning.

Why embrace StudyHub? Let's break it down:

- 🤝 Connect and Conquer: Ever felt stuck while studying? StudyHub breaks the ice, connecting you with fellow students who share your quest for knowledge. Collaboration has never been cooler.

- 🌟 AI Magic at Your Service: Say goodbye to one-size-fits-all solutions. StudyHub's AI wizardry tailors its offerings just for you. From automated essay grading to customized concept explanations, it's like having your own virtual tutor, but way cooler.

- 💬 Chatter That Matters: Imagine engaging in academic discussions that light up your neurons. StudyHub's social vibes fuel meaningful conversations, sparking insights you won't find in a textbook.

- 📚 All-Inclusive Academic Oasis: No more frantic browser hopping for resources. StudyHub wraps it all up – academic consultation, resources, and discussions – in a user-friendly package. A one-stop shop for your learning journey.

- 🧠 By Learners, for Learners: We're not just tech enthusiasts; we're learners too. Your feedback is our rocket fuel. StudyHub's user-centric evolution ensures we stay ahead of your learning curve.

Ready to level up your learning game? Say hello to StudyHub, where AI meets education, and collaboration takes the spotlight. Let's learn, connect, and conquer together! 🚀

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With



* [![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Getting Started -->

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development. See deployment for notes on how to deploy the project.

### Prerequisites

- [Python](https://www.python.org/) (3.9 Recommended)
- AWS S3 Bucket on [Amazon Web Services](https://aws.amazon.com/)
- [OpenAI API Key](https://platform.openai.com/account/api-keys)
- [Pinecone API Key & Index Name](https://www.pinecone.io/)

### Local Setup

1. Clone the repository.
```shell
git clone https://github.com/TheTrustyPwo/StudyHub.git
```

2. Set up a `venv` and use `pip` to install the project dependencies.
```shell
cd StudyHub
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure the [config.py](https://github.com/TheTrustyPwo/StudyHub/blob/master/app/config.py) if necessary.

4. Set the required environment variables and start the app. Now you can give the application a try at [http://localhost:5000](http://localhost:5000)!

```shell
export AWS_ACCESS_KEY=key
export AWS_SECRET_ACCESS_KEY=key
export PINECONE_API_KEY=key
flask run
```

You can also serve the application using [gunicorn](https://gunicorn.org/).

```shell
gunicorn "app:create_app()"
```

### Testing

Test the application with the custom script.
```shell
python test.py
```

### Deployment

*Coming Soon*

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the GNU GPLv3 License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTACT -->

## Contact

TheTrustyPwo - Pwo#0001 - thetrustypwo@gmail.com

Project Link: [https://github.com/TheTrustyPwo/StudyHub](https://github.com/TheTrustyPwo/StudyHub)

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->

[contributors-shield]: https://img.shields.io/github/contributors/TheTrustyPwo/StudyHub.svg?style=for-the-badge

[contributors-url]: https://github.com/TheTrustyPwo/StudyHub/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/TheTrustyPwo/StudyHub.svg?style=for-the-badge

[forks-url]: https://github.com/TheTrustyPwo/StudyHub/network/members

[stars-shield]: https://img.shields.io/github/stars/TheTrustyPwo/StudyHub.svg?style=for-the-badge

[stars-url]: https://github.com/TheTrustyPwo/StudyHub/stargazers

[issues-shield]: https://img.shields.io/github/issues/TheTrustyPwo/StudyHub.svg?style=for-the-badge

[issues-url]: https://github.com/TheTrustyPwo/StudyHub/issues

[license-shield]: https://img.shields.io/github/license/TheTrustyPwo/StudyHub.svg?style=for-the-badge

[license-url]: https://github.com/TheTrustyPwo/StudyHub/blob/master/LICENSE.txt