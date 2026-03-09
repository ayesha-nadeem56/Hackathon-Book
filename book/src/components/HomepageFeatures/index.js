import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

/**
 * T007: Book-specific feature cards — replaced Docusaurus placeholder content.
 * Icons use Unicode emoji as inline fallbacks (no SVG file dependencies).
 */
const FeatureList = [
  {
    icon: '🤖',
    title: 'ROS 2 & Physical AI',
    description:
      'From ROS 2 fundamentals to full humanoid robot pipelines — build, simulate, and deploy autonomous physical AI systems step by step.',
  },
  {
    icon: '💬',
    title: 'AI-Powered RAG Chatbot',
    description:
      "Ask questions about any chapter using an embedded Retrieval-Augmented Generation chatbot grounded in the book's full content corpus.",
  },
  {
    icon: '🧪',
    title: 'Hands-On Code Examples',
    description:
      'Every concept is backed by reproducible Python code — version-pinned, tested, and annotated so you can follow along on your own hardware.',
  },
];

function Feature({icon, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className={styles.featureCard}>
        <span className={styles.featureIcon} role="img" aria-label={title}>
          {icon}
        </span>
        <div className="text--center padding-horiz--sm">
          <Heading as="h3">{title}</Heading>
          <p>{description}</p>
        </div>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
