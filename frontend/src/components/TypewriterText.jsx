import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

export default function TypewriterText({ text, speed = 8 }) {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    // Reset when text changes
    setDisplayedText('');
    let i = 0;
    
    // Typewriter effect interval
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayedText((prev) => prev + text.charAt(i));
        i++;
      } else {
        clearInterval(timer);
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed]);

  return (
    // The "prose" class from Tailwind Typography automatically formats Markdown beautifully
    <div className="prose prose-indigo prose-sm md:prose-base max-w-none text-gray-700 leading-relaxed">
      <ReactMarkdown>{displayedText}</ReactMarkdown>
    </div>
  );
}
