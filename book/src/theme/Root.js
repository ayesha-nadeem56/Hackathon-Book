import React from 'react';
import ChatWidget from '@site/src/components/ChatWidget';

/**
 * Root swizzle — wraps the entire Docusaurus application.
 * ChatWidget is rendered after all page content so it appears on every route
 * (home, /docs/*, blog, etc.) without modifying any individual page files.
 */
export default function Root({ children }) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}
