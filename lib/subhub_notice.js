var rule = {
    title: 'subHub',
    host: 'https://github.com/SakuraByteCore/subHub',
    homeUrl: '',
    url: '/fyclass',
    searchUrl: '',
    searchable: 1,
    quickSearch: 0,
    filterable: 0,
    class_name: '项目说明&订阅链接&当前输出&来源说明',
    class_url: 'about&links&outputs&sources',
    headers: {
        'User-Agent': 'Mozilla/5.0'
    },
    推荐: `js:
        let d = [{
            title: 'subHub | 公共订阅与配置源聚合入口',
            img: '',
            desc: '当前第一类输出是 TVBox；后续可扩展 IPTV、代理订阅和其它客户端配置。',
            url: 'about'
        }, {
            title: 'TVBox 订阅入口',
            img: '',
            desc: 'https://sakurabytecore.github.io/subHub/tvbox.json',
            url: 'links'
        }];
        setResult(d);
    `,
    一级: `js:
        let cards = {
            about: [{
                title: 'subHub | 公共订阅与配置源聚合入口',
                img: '',
                desc: '聚合公开订阅和配置源，规范化、去重后生成可直接使用的输出文件。',
                url: 'about'
            }],
            links: [{
                title: 'TVBox 主订阅链接（GitHub Pages）',
                img: '',
                desc: 'GitHub Pages / tvbox.json',
                url: 'https://sakurabytecore.github.io/subHub/tvbox.json'
            }, {
                title: 'TVBox 备用链接 jsDelivr',
                img: '',
                desc: 'cdn.jsdelivr.net / refs/heads/main / tvbox.json',
                url: 'https://cdn.jsdelivr.net/gh/SakuraByteCore/subHub@refs/heads/main/tvbox.json'
            }, {
                title: 'TVBox 备用链接 Fastly',
                img: '',
                desc: 'fastly.jsdelivr.net / refs/heads/main / tvbox.json',
                url: 'https://fastly.jsdelivr.net/gh/SakuraByteCore/subHub@refs/heads/main/tvbox.json'
            }, {
                title: 'TVBox 备用链接 Gcore',
                img: '',
                desc: 'gcore.jsdelivr.net / refs/heads/main / tvbox.json',
                url: 'https://gcore.jsdelivr.net/gh/SakuraByteCore/subHub@refs/heads/main/tvbox.json'
            }],
            outputs: [{
                title: '当前输出：TVBox JSON',
                img: '',
                desc: 'GitHub Pages 固定入口会发布 tvbox.json、manifest.json 和公告脚本。',
                url: 'outputs'
            }],
            sources: [{
                title: '来源配置：sources.json',
                img: '',
                desc: '当前来源类型为 tvbox，后续可继续增加 iptv、proxy、mixed 等类型。',
                url: 'sources'
            }]
        };
        setResult(cards[MY_CATE] || cards.about);
    `,
    二级: `js:
        let content = 'subHub 是公共订阅与配置源聚合入口。当前第一类输出是 TVBox 配置，后续可以扩展 IPTV、代理订阅、sing-box、mihomo 或其它客户端配置。\\n\\nTVBox 主链接：\\nhttps://sakurabytecore.github.io/subHub/tvbox.json\\n\\n备用：\\nhttps://cdn.jsdelivr.net/gh/SakuraByteCore/subHub@refs/heads/main/tvbox.json\\nhttps://fastly.jsdelivr.net/gh/SakuraByteCore/subHub@refs/heads/main/tvbox.json\\nhttps://gcore.jsdelivr.net/gh/SakuraByteCore/subHub@refs/heads/main/tvbox.json';
        VOD = {
            vod_id: input,
            vod_name: 'subHub | 公共订阅与配置源聚合入口',
            vod_pic: '',
            type_name: 'subHub',
            vod_year: '',
            vod_area: '',
            vod_remarks: '订阅聚合',
            vod_actor: 'SakuraByteCore/subHub',
            vod_director: 'subHub',
            vod_content: content,
            vod_play_from: '说明',
            vod_play_url: '项目主页$https://github.com/SakuraByteCore/subHub'
        };
    `,
    搜索: `js:
        let wd = KEY || '';
        setResult([{
            title: 'subHub | 公共订阅聚合',
            img: '',
            desc: wd ? ('搜索词：' + wd + '。这里是 subHub 公告源，用于展示订阅入口；影视搜索请切换到其它站点。') : '这里是 subHub 公告源，用于展示订阅入口；影视搜索请切换到其它站点。',
            url: 'about'
        }]);
    `,
    lazy: `js:
        input = {parse: 0, url: input};
    `
};
