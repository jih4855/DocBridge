/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  transpilePackages: ['react-markdown', 'remark-gfm', 'mermaid', 'react-syntax-highlighter', 'rehype-highlight', 'micromark', 'unist-util-visit', 'mdast-util-from-markdown', 'devlop', 'vfile', 'vfile-message', 'unist-util-stringify-position', 'micromark-util-character', 'micromark-util-chunked', 'micromark-util-combine-extensions', 'micromark-util-decode-numeric-character-reference', 'micromark-util-encode', 'micromark-util-normalize-identifier', 'micromark-util-resolve-all', 'micromark-util-sanitize-uri', 'micromark-util-string-line', 'micromark-util-symbol', 'micromark-util-html-tag-name', 'mdast-util-to-hast', 'mdast-util-to-string', 'micromark-core-commonmark', 'unified', 'bail', 'trough', 'is-plain-obj', 'decode-named-character-reference', 'character-entities', 'property-information', 'space-separated-tokens', 'comma-separated-tokens', 'web-namespaces', 'hast-util-whitespace', 'hast-util-to-html', 'html-void-elements', 'ccount', 'escape-string-regexp', 'markdown-table', 'hast-util-to-jsx-runtime', 'estree-util-is-identifier-name', 'unist-util-position'],
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
