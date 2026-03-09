// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'AI-Driven Interactive Book',
  tagline: 'Humanoid Robotics and Physical AI — from ROS 2 to RAG',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  // GitHub Pages deployment config
  url: 'https://hackathon-book-voxj-ptgkmls62-ayesha-nadeems-projects-862e44cf.vercel.app/',
  baseUrl: "/",
  organizationName: 'ayesha-nadeem56',
  projectName: 'Hackathon-Book',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  // Enable Mermaid diagram rendering
  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          routeBasePath: 'docs',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      mermaid: {
        theme: {light: 'neutral', dark: 'dark'},
      },
      navbar: {
        title: 'AI-Driven Interactive Book',
        logo: {
          alt: 'Book Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'bookSidebar',
            position: 'left',
            label: 'Chapters',
          },
          {
            href: 'https://github.com/ayesha-nadeem56/Hackathon-Book',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Book',
            items: [
              {
                label: 'All Chapters',
                to: '/docs/module-1-ros2/',
              },
              {
                label: 'Module 1 — ROS 2',
                to: '/docs/module-1-ros2/',
              },
            ],
          },
          {
            title: 'Project',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/ayesha-nadeem56/Hackathon-Book',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} AI-Driven Interactive Book. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'yaml', 'docker'],
      },
    }),
};

export default config;
