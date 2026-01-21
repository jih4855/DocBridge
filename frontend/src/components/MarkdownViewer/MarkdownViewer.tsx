'use client';

import React, { useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import mermaid from 'mermaid';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check } from 'lucide-react';
import { useState } from 'react';

// Initialize mermaid
mermaid.initialize({
    startOnLoad: false,
    theme: 'dark',
    securityLevel: 'loose',
});

interface MarkdownViewerProps {
    content: string;
    className?: string;
}

export default function MarkdownViewer({ content, className }: MarkdownViewerProps) {
    useEffect(() => {
        // Run mermaid on .mermaid elements
        mermaid.run({
            querySelector: '.mermaid'
        });
    }, [content]);

    return (
        <div className={`prose prose-invert max-w-none ${className || ''}`}>
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                    code({ node, inline, className, children, ...props }: any) {
                        const match = /language-(\w+)/.exec(className || '');
                        const language = match ? match[1] : '';
                        const codeString = String(children).replace(/\n$/, '');

                        // 1. Mermaid Diagram
                        if (!inline && language === 'mermaid') {
                            return (
                                <div className="mermaid bg-transparent my-4 flex justify-center">
                                    {codeString}
                                </div>
                            );
                        }

                        // 2. Code Block with Syntax Highlighting
                        if (!inline && match) {
                            return (
                                <CodeBlock
                                    language={language}
                                    value={codeString}
                                    {...props}
                                />
                            );
                        }

                        // 3. Inline Code
                        return (
                            <code className={className} {...props}>
                                {children}
                            </code>
                        );
                    }
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    );
}

// Separate component to handle copy state
function CodeBlock({ language, value, ...props }: { language: string, value: string }) {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        await navigator.clipboard.writeText(value);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="relative group rounded-md overflow-hidden bg-[#1e1e1e] border border-[#333] my-4">
            {/* Copy Button */}
            <button
                onClick={handleCopy}
                className="absolute right-2 top-2 p-1.5 rounded-md bg-[#2d2d2d] text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity hover:text-white"
                title="Copy code"
            >
                {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
            </button>

            <SyntaxHighlighter
                style={vscDarkPlus}
                language={language}
                PreTag="div"
                customStyle={{
                    margin: 0,
                    borderRadius: 0,
                    fontSize: '0.875rem',
                    lineHeight: '1.5',
                    background: 'transparent' // Use parent bg
                }}
                {...props}
            >
                {value}
            </SyntaxHighlighter>
        </div>
    );
}
