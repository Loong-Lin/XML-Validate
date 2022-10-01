<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
    <html>
        <head>
            <title>BookStore</title>
            <body>
                <xsl:apply-templates select="bookstore"/>
            </body>
        </head>
    </html>
</xsl:template>

<xsl:template match="bookstore">
    <xsl:apply-templates select="book"/>
</xsl:template>

<xsl:template match="book">
    <h2>
      Category: <xsl:value-of select="category"/>
    </h2>
    <p>
        Title: <xsl:value-of select="title"/>
        Authors: <xsl:value-of select="author"/>
        Year: <xsl:value-of select="year"/>
        Price: <xsl:value-of select="price"/>
    </p>
</xsl:template>
</xsl:stylesheet>