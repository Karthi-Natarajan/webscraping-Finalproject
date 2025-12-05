import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className='footer'>
      <p>© 2023 Product Sentiment Analyzer. All rights reserved.</p>
      <div className='footer-links'>
        <a href='/about'>About</a>
        <a href='/privacy'>Privacy</a>
        <a href='/terms'>Terms</a>
      </div>
    </footer>
  );
};

export default Footer;