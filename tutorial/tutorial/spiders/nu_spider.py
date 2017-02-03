import scrapy

class NUSpider(scrapy.Spider):
    name = "NovelUpdates"

    def start_requests(self):
        urls = ['http://www.novelupdates.com']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def shinsori_parse(self, response):
        for title in response.css('.entry-title::text'):
            yield response.meta['item']

    def wuxiaworld_parse(self, response):
        urls = response.css('div.chapterBtn>a::attr(href)')
        if urls is None:
            urls = response.css('div[itemprop=articleBody] a::attr(href)')

        for url in urls:
            print 'wuxiaworld:%s' % url.extract()
            request = scrapy.Request(url = response.urljoin(url.extract()), callback=self.wuxiaworld_chapter_parse)
            request.meta['item'] = response.meta['item']
            yield request

    def wuxiaworld_chapter_parse(self, response):
        body = response.css('div[itemprop=articleBody]').extract()
        print "content len:%d" % len(body)
        item = response.meta['item']
        yield {'title':item['title'], 'chapter':item['chapter'],
                'group':item['group']}
    
    def parse(self, response):
        for series in response.css('#myTable>tbody>tr'):
            infos = series.css('td')
            title = infos[0].css('a::text').extract_first()
            chapter = infos[1].css('a::text').extract_first()
            url = infos[1].css('a.chp-release::attr(href)').extract_first()
            next_page = response.urljoin(url)
            group = infos[2].css('a::text').extract_first()
            item = {}
            item['chapter'] = chapter
            item['title'] = title
            item['group'] = group

            callback = self.shinsori_parse
            if group == 'Shinsori Translations':
                callback = self.shinsori_parse
                continue
            elif group == 'Wuxiaworld':
                callback = self.wuxiaworld_parse
                print next_page
                print infos[1].extract()
            else:
                continue

            request = scrapy.Request(url=next_page, callback=callback)
            request.meta['item'] = item
            yield request
            #yield { 'title':title.extract(), 'chapter':'author'}
