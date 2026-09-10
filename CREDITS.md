# Credits

The detector shipped in `src/grooveclean/weights/detector.pt` was trained on audio from
the Internet Archive. Clicks came from the [78rpm](https://archive.org/details/78rpm)
collection, whose transfers are of recordings in the public domain in the United States.
Clean music came from the [netlabels](https://archive.org/details/netlabels) collection,
released by its artists under Creative Commons and similar licences.

What ships is mostly a set of network weights. The audio that is checked in is
`tests/data/excerpt78.flac` and `tests/data/clean_excerpt.flac`, both credited in
`tests/data/ASSETS.json`, and `tests/data/detector_eval.flac`, whose music is drawn
only from the public domain and CC-BY items in the table below.

Items marked `test` were held out of training and used only to score the detector.

## Clicks: 530 78rpm transfers, 470,701 click waveforms

| Item | Clicks | Split |
| --- | --- | --- |
| [62876-schlusnus-freundliche-vision](https://archive.org/details/62876-schlusnus-freundliche-vision) | 19 | train |
| [78_a-oi-letila-gorlitsia-a-a-turtle-was-flying-b-i-shumit-i-gudie-b-theres_gbia0429634a](https://archive.org/details/78_a-oi-letila-gorlitsia-a-a-turtle-was-flying-b-i-shumit-i-gudie-b-theres_gbia0429634a) | 681 | train |
| [78_clair-de-lune-op-83-no-1_maggie-teyte-gerald-moore-verlaine-szulc_gbia0525309a](https://archive.org/details/78_clair-de-lune-op-83-no-1_maggie-teyte-gerald-moore-verlaine-szulc_gbia0525309a) | 2000 | test |
| [78_clementine_bix-beiderbecke-jean-goldkette-his-orchestra-creamer-warren_gbia0552734a](https://archive.org/details/78_clementine_bix-beiderbecke-jean-goldkette-his-orchestra-creamer-warren_gbia0552734a) | 224 | test |
| [78_cleveland-slovene-polka_cosmopolitan-orchestra_gbia0425162a](https://archive.org/details/78_cleveland-slovene-polka_cosmopolitan-orchestra_gbia0425162a) | 3 | train |
| [78_coffee-bean-calypso_the-grosvenor-studio-orchestra-a-pinto-dolf-van-der-linden_gbia3009867a](https://archive.org/details/78_coffee-bean-calypso_the-grosvenor-studio-orchestra-a-pinto-dolf-van-der-linden_gbia3009867a) | 474 | train |
| [78_cogs-in-commotion_the-symphonia-orchestra-ken-morrison-curt-andersen_gbia3015928b](https://archive.org/details/78_cogs-in-commotion_the-symphonia-orchestra-ken-morrison-curt-andersen_gbia3015928b) | 187 | train |
| [78_come-into-my-arms_chuck-cabot-and-his-orchestra-lynn-avalon-cabot-murphy-detra_gbia0468458a](https://archive.org/details/78_come-into-my-arms_chuck-cabot-and-his-orchestra-lynn-avalon-cabot-murphy-detra_gbia0468458a) | 107 | train |
| [78_comedy-links-82-88_new-century-orchestra-robert-early-erich-brschel_gbia3012187b](https://archive.org/details/78_comedy-links-82-88_new-century-orchestra-robert-early-erich-brschel_gbia3012187b) | 1249 | train |
| [78_command-performance_al-bollington_gbia7019342b](https://archive.org/details/78_command-performance_al-bollington_gbia7019342b) | 596 | train |
| [78_commeautrefoisdanslanuitsombre_328_16](https://archive.org/details/78_commeautrefoisdanslanuitsombre_328_16) | 2000 | test |
| [78_comment-on-a-sad-occasion_the-new-concert-orchestra-eugene-cines_gbia3033829b](https://archive.org/details/78_comment-on-a-sad-occasion_the-new-concert-orchestra-eugene-cines_gbia3033829b) | 1361 | train |
| [78_concerto-no-1-in-b-flat-minor-1st-movement-part-3_vladimir-horowitz-arturo-toscanin_gbia7042522a](https://archive.org/details/78_concerto-no-1-in-b-flat-minor-1st-movement-part-3_vladimir-horowitz-arturo-toscanin_gbia7042522a) | 2000 | train |
| [78_concordia-conclusion_cbc-orchestra-alexander-brott-jean-beaudet_gbia3021096b](https://archive.org/details/78_concordia-conclusion_cbc-orchestra-alexander-brott-jean-beaudet_gbia3021096b) | 2000 | train |
| [78_coolee-dam_woody-guthrie_gbia8005778](https://archive.org/details/78_coolee-dam_woody-guthrie_gbia8005778) | 435 | train |
| [78_cowboy-medley_bill-bender-the-happy-cowboy_gbia0057168b](https://archive.org/details/78_cowboy-medley_bill-bender-the-happy-cowboy_gbia0057168b) | 470 | train |
| [78_creation-and-redemption_gbia3009892b](https://archive.org/details/78_creation-and-redemption_gbia3009892b) | 42 | train |
| [78_czardas_freddy-balta-monti-f-balta_gbia0447780b](https://archive.org/details/78_czardas_freddy-balta-monti-f-balta_gbia0447780b) | 86 | train |
| [78_czy-pamitasz-tinker-polka_siostry-lazarz-s-lazarz_gbia0531345a](https://archive.org/details/78_czy-pamitasz-tinker-polka_siostry-lazarz-s-lazarz_gbia0531345a) | 39 | test |
| [78_dance-of-the-red-skins_todd-rhodes-orchestra-rhodes-todd-rhodes-joe-williams-hueste_gbia0119841b](https://archive.org/details/78_dance-of-the-red-skins_todd-rhodes-orchestra-rhodes-todd-rhodes-joe-williams-hueste_gbia0119841b) | 2000 | train |
| [78_dance-time-no-3_victor-silvester-his-ballroom-orchestra_gbia3002114b](https://archive.org/details/78_dance-time-no-3_victor-silvester-his-ballroom-orchestra_gbia3002114b) | 1509 | train |
| [78_danse-macabre-dance-of-death-part-ii_leopold-stokowski-and-the-philadelphia-orchest_gbia7042700b](https://archive.org/details/78_danse-macabre-dance-of-death-part-ii_leopold-stokowski-and-the-philadelphia-orchest_gbia7042700b) | 219 | train |
| [78_danse-magique_constantin-brailoiu-prof-j-gabus_gbia0057690a](https://archive.org/details/78_danse-magique_constantin-brailoiu-prof-j-gabus_gbia0057690a) | 92 | train |
| [78_dark-depths_paul-franklin-his-orchestra-edward-lockspeiser_gbia3008495b](https://archive.org/details/78_dark-depths_paul-franklin-his-orchestra-edward-lockspeiser_gbia3008495b) | 126 | train |
| [78_das-veilchen-the-violet-k476_elisabeth-schumann-gerald-moore-goethe-mozart_gbia0196524a](https://archive.org/details/78_das-veilchen-the-violet-k476_elisabeth-schumann-gerald-moore-goethe-mozart_gbia0196524a) | 2000 | train |
| [78_de-sier-du-kan-li-mig_sid-merrimans-danseorkester-eddie-russell-jens-dennow_gbia7010875a](https://archive.org/details/78_de-sier-du-kan-li-mig_sid-merrimans-danseorkester-eddie-russell-jens-dennow_gbia7010875a) | 647 | train |
| [78_deems-dem-and-dose_ed-archie-gardner-deems-taylor_gbia0095314b](https://archive.org/details/78_deems-dem-and-dose_ed-archie-gardner-deems-taylor_gbia0095314b) | 570 | train |
| [78_deems-dem-and-dose_ed-archie-gardner-deems-tayor_gbia0415546b](https://archive.org/details/78_deems-dem-and-dose_ed-archie-gardner-deems-tayor_gbia0415546b) | 363 | train |
| [78_deep-in-my-heart-dear_mario-lanza-elizabeth-doubleday-constantine-callinicos-don_gbia7034515b](https://archive.org/details/78_deep-in-my-heart-dear_mario-lanza-elizabeth-doubleday-constantine-callinicos-don_gbia7034515b) | 2000 | train |
| [78_der-doppelgnger_kipnis-alexander-bibb-frank](https://archive.org/details/78_der-doppelgnger_kipnis-alexander-bibb-frank) | 1 | train |
| [78_der-mller-und-der-bach-die-schne-mllerin_duhan-hans-foll-ferdinand](https://archive.org/details/78_der-mller-und-der-bach-die-schne-mllerin_duhan-hans-foll-ferdinand) | 3 | train |
| [78_die-ehrenwache_lehnhardt_gbia0072701b](https://archive.org/details/78_die-ehrenwache_lehnhardt_gbia0072701b) | 813 | train |
| [78_dirty-dirty-dirty_the-morton-seven-morton-red-allen-claude-jones-albert-nicholas_gbia0023032a](https://archive.org/details/78_dirty-dirty-dirty_the-morton-seven-morton-red-allen-claude-jones-albert-nicholas_gbia0023032a) | 264 | train |
| [78_dixieland-ball_eileen-barton-b-kaye-a-frisch_gbia0238268b](https://archive.org/details/78_dixieland-ball_eileen-barton-b-kaye-a-frisch_gbia0238268b) | 376 | train |
| [78_dnes-a-do-rna_krlovsk-prim-jojo-galbavy-s-jeho-cigaskou-kapelou-kritof-vese_gbia0184334a](https://archive.org/details/78_dnes-a-do-rna_krlovsk-prim-jojo-galbavy-s-jeho-cigaskou-kapelou-kritof-vese_gbia0184334a) | 730 | train |
| [78_do-dek-e-moma-pri-majka_elena-mukaetova-maliot-radio-orchestar_gbia0512597a](https://archive.org/details/78_do-dek-e-moma-pri-majka_elena-mukaetova-maliot-radio-orchestar_gbia0512597a) | 1785 | train |
| [78_doch-dass-der-arme-yet-did-gods-angel_elisabeth-rethberg-wagner_gbia0077721b](https://archive.org/details/78_doch-dass-der-arme-yet-did-gods-angel_elisabeth-rethberg-wagner_gbia0077721b) | 1629 | train |
| [78_doch-es-rchte-sich-der-verscheuchte-tag-but-its-vengeance_frida-leider-lauritz-m_gbia7027463b](https://archive.org/details/78_doch-es-rchte-sich-der-verscheuchte-tag-but-its-vengeance_frida-leider-lauritz-m_gbia7027463b) | 2000 | train |
| [78_donaublger-donauwellen_the-blue-hungarian-band-ivanovici_gbia0123895a](https://archive.org/details/78_donaublger-donauwellen_the-blue-hungarian-band-ivanovici_gbia0123895a) | 991 | train |
| [78_donauwellen_mitglieder-des-berliner-philharmonischen-orchesters-i-ivanovici_gbia0184403a](https://archive.org/details/78_donauwellen_mitglieder-des-berliner-philharmonischen-orchesters-i-ivanovici_gbia0184403a) | 1566 | train |
| [78_donauwellen_roland-blair-ivanovici_gbia0540366b](https://archive.org/details/78_donauwellen_roland-blair-ivanovici_gbia0540366b) | 989 | train |
| [78_dont-blame-me_jack-mcvea-and-his-all-stars-jack-mcvea-bob-mosley-frank-clarke-rabo_gbia0118917b](https://archive.org/details/78_dont-blame-me_jack-mcvea-and-his-all-stars-jack-mcvea-bob-mosley-frank-clarke-rabo_gbia0118917b) | 1108 | train |
| [78_dont-blame-me_sarah-vaughan-george-treadwells-orchestra-fields-mchugh_gbia0189092b](https://archive.org/details/78_dont-blame-me_sarah-vaughan-george-treadwells-orchestra-fields-mchugh_gbia0189092b) | 706 | train |
| [78_dont-bring-lulu-no-lleve-ud-a-lulu_varsity-eight-dixon-rose-brown_gbia0334926a](https://archive.org/details/78_dont-bring-lulu-no-lleve-ud-a-lulu_varsity-eight-dixon-rose-brown_gbia0334926a) | 719 | train |
| [78_dont-do-it_al-lombardi-quintet-four-jacks-and-a-jill-poppy-marin-stevens-tempo-pia_gbia0408410a](https://archive.org/details/78_dont-do-it_al-lombardi-quintet-four-jacks-and-a-jill-poppy-marin-stevens-tempo-pia_gbia0408410a) | 23 | train |
| [78_dont-forbid-me-love-me_don-dean-arch-angel-singleton-leiber-stoller_gbia0549275a](https://archive.org/details/78_dont-forbid-me-love-me_don-dean-arch-angel-singleton-leiber-stoller_gbia0549275a) | 59 | train |
| [78_dont-forget-me-little-darling_dave-miller_gbia0006896b](https://archive.org/details/78_dont-forget-me-little-darling_dave-miller_gbia0006896b) | 375 | train |
| [78_dont-forget-me_frank-yankovic-and-his-orchestra-don-h-gabor_gbia0241969a](https://archive.org/details/78_dont-forget-me_frank-yankovic-and-his-orchestra-don-h-gabor_gbia0241969a) | 251 | test |
| [78_dont-forget-the-old-folks-at-home_billy-thorburn-his-music-noel-pelosi_gbia3002178a](https://archive.org/details/78_dont-forget-the-old-folks-at-home_billy-thorburn-his-music-noel-pelosi_gbia3002178a) | 576 | train |
| [78_dont-give-me-the-runaround_t-bone-walker-and-his-guitar-al-killian-quintet-walker_gbia0365354a](https://archive.org/details/78_dont-give-me-the-runaround_t-bone-walker-and-his-guitar-al-killian-quintet-walker_gbia0365354a) | 173 | test |
| [78_dont-let-our-love-die-on-the-vine_polly-bergen-johnny-richards-ralph-freed-jerry-l_gbia0004060b](https://archive.org/details/78_dont-let-our-love-die-on-the-vine_polly-bergen-johnny-richards-ralph-freed-jerry-l_gbia0004060b) | 525 | train |
| [78_dont-wait-up-for-me_sylvia-syms-larry-clinton-and-his-orchestra-de-forest_gbia0563409b](https://archive.org/details/78_dont-wait-up-for-me_sylvia-syms-larry-clinton-and-his-orchestra-de-forest_gbia0563409b) | 600 | train |
| [78_dont-you-feel-my-leg_danny-barker-sextette-blu-lu-barker-danny-barker_gbia0175537a](https://archive.org/details/78_dont-you-feel-my-leg_danny-barker-sextette-blu-lu-barker-danny-barker_gbia0175537a) | 79 | train |
| [78_dort-wo-du-hingehst_erhard-bauschke-tanz-orchester-kreuder-beckmann_gbia0254156b](https://archive.org/details/78_dort-wo-du-hingehst_erhard-bauschke-tanz-orchester-kreuder-beckmann_gbia0254156b) | 927 | train |
| [78_doudlebska-polka_michael-hermans-folk-orchestra_gbia0047800b](https://archive.org/details/78_doudlebska-polka_michael-hermans-folk-orchestra_gbia0047800b) | 1155 | train |
| [78_doughnuts-with-the-hole-in-the-middle_leonard-ware-trio-leonard-ware-willie-spott_gbia0007729a](https://archive.org/details/78_doughnuts-with-the-hole-in-the-middle_leonard-ware-trio-leonard-ware-willie-spott_gbia0007729a) | 388 | train |
| [78_down-home-in-tennessee_mr-herbert-payne-donaldson_gbia3035920b](https://archive.org/details/78_down-home-in-tennessee_mr-herbert-payne-donaldson_gbia3035920b) | 536 | train |
| [78_dramatic-love-theme_the-london-promenade-orchestra-walter-collins-f-g-charrosin_gbia3019399a](https://archive.org/details/78_dramatic-love-theme_the-london-promenade-orchestra-walter-collins-f-g-charrosin_gbia3019399a) | 2000 | train |
| [78_dreamy-tokyo_gbia0277553a](https://archive.org/details/78_dreamy-tokyo_gbia0277553a) | 212 | train |
| [78_dry-your-eyes_walt-shrum-and-his-colorado-hillbillies-blair-hoag-dean_gbia0219647b](https://archive.org/details/78_dry-your-eyes_walt-shrum-and-his-colorado-hillbillies-blair-hoag-dean_gbia0219647b) | 25 | test |
| [78_du-bist-verkehrt-verheirat-_adalbert-lutter-mit-seinem-orchester-erwin-hartun_gbia0435756b](https://archive.org/details/78_du-bist-verkehrt-verheirat-_adalbert-lutter-mit-seinem-orchester-erwin-hartun_gbia0435756b) | 579 | train |
| [78_egg-flip_the-symphonia-orchestra-peter-dennis-ludo-philipp_gbia3016522a](https://archive.org/details/78_egg-flip_the-symphonia-orchestra-peter-dennis-ludo-philipp_gbia3016522a) | 748 | test |
| [78_egmont-ouverture-opus-84-2_det-kongelige-kapel-beethoven-pierino-gamba_gbia7013089b](https://archive.org/details/78_egmont-ouverture-opus-84-2_det-kongelige-kapel-beethoven-pierino-gamba_gbia7013089b) | 1046 | test |
| [78_eileen-alannah_jimmy-shand-and-his-band-j-r-thomas-shand_gbia3029274a](https://archive.org/details/78_eileen-alannah_jimmy-shand-and-his-band-j-r-thomas-shand_gbia3029274a) | 83 | train |
| [78_eileen-alannah_phillip-ritte_gbia3007853a](https://archive.org/details/78_eileen-alannah_phillip-ritte_gbia3007853a) | 128 | train |
| [78_ein-walzertraum_g-ernesto_gbia7035898a](https://archive.org/details/78_ein-walzertraum_g-ernesto_gbia7035898a) | 244 | train |
| [78_eine-kleine-nachtmusik-3-del_emil-telmanyi-med-sit-kammerorkester-mozart_gbia7012992a](https://archive.org/details/78_eine-kleine-nachtmusik-3-del_emil-telmanyi-med-sit-kammerorkester-mozart_gbia7012992a) | 585 | train |
| [78_einsam-in-trben-tagen-elsas-dream_maria-jeritza-wagner_gbia7003651a](https://archive.org/details/78_einsam-in-trben-tagen-elsas-dream_maria-jeritza-wagner_gbia7003651a) | 2000 | train |
| [78_el-mexicano_noe-fajardo-lorenzo-bravo-y-agustin-islas-narciso-martinez_gbia0064080a](https://archive.org/details/78_el-mexicano_noe-fajardo-lorenzo-bravo-y-agustin-islas-narciso-martinez_gbia0064080a) | 1408 | train |
| [78_elfinette_sidney-torch-and-his-orchestra-jansen_gbia3034932b](https://archive.org/details/78_elfinette_sidney-torch-and-his-orchestra-jansen_gbia3034932b) | 2000 | train |
| [78_ellenecroyaitpas_211_11](https://archive.org/details/78_ellenecroyaitpas_211_11) | 354 | test |
| [78_embraceable-you-c_neely-plumb-and-his-orchestra-stan-wrightsman-bob-simmers-nick_gbia0401460a](https://archive.org/details/78_embraceable-you-c_neely-plumb-and-his-orchestra-stan-wrightsman-bob-simmers-nick_gbia0401460a) | 77 | train |
| [78_en-susande-brusande-hambo_sigurd-grens-harmonika-orkester-jerry-hgstedt_gbia7007470b](https://archive.org/details/78_en-susande-brusande-hambo_sigurd-grens-harmonika-orkester-jerry-hgstedt_gbia7007470b) | 801 | train |
| [78_en-trainant-la-savate_eddie-barclay-et-les-careno-cuban-boys-salvador-et-pon_gbia0399898a](https://archive.org/details/78_en-trainant-la-savate_eddie-barclay-et-les-careno-cuban-boys-salvador-et-pon_gbia0399898a) | 92 | train |
| [78_enfin-lprintemps_charles-verstraete-et-son-ensemble-musette-monnot_gbia0408362b](https://archive.org/details/78_enfin-lprintemps_charles-verstraete-et-son-ensemble-musette-monnot_gbia0408362b) | 117 | train |
| [78_engang-vil-solen-skinne-somewhere-a-voice-is-calling_brge-lvenfalk-arthur-f-tate-he_gbia7036102b](https://archive.org/details/78_engang-vil-solen-skinne-somewhere-a-voice-is-calling_brge-lvenfalk-arthur-f-tate-he_gbia7036102b) | 1321 | train |
| [78_jecroisentendreencore_068_16](https://archive.org/details/78_jecroisentendreencore_068_16) | 425 | train |
| [78_karavan_joseph-c-smiths-orchestra-olman-wiedoeft_gbia3033222b](https://archive.org/details/78_karavan_joseph-c-smiths-orchestra-olman-wiedoeft_gbia3033222b) | 104 | train |
| [78_kom-til-mig-med-krlighed_erik-michaelsen-willy-srensens-orkester-mark-paul-knud-p_gbia7011058b](https://archive.org/details/78_kom-til-mig-med-krlighed_erik-michaelsen-willy-srensens-orkester-mark-paul-knud-p_gbia7011058b) | 972 | test |
| [78_listen-to-the-lambs_rollins-chapel-choir-bach-christopher-o-honaas_gbia0071985](https://archive.org/details/78_listen-to-the-lambs_rollins-chapel-choir-bach-christopher-o-honaas_gbia0071985) | 1788 | train |
| [78_not-a-little-autumn-rain_d-aristoff-choir_gbia0538768b](https://archive.org/details/78_not-a-little-autumn-rain_d-aristoff-choir_gbia0538768b) | 2000 | test |
| [78_oh-what-a-beautiful-morning_marcel-pagnoul-son-orchestre-richard-rodgers_gbia0402905b](https://archive.org/details/78_oh-what-a-beautiful-morning_marcel-pagnoul-son-orchestre-richard-rodgers_gbia0402905b) | 856 | train |
| [78_rhythm-time-records-album-1_elizabeth-l-sehon-emma-lou-obrien_gbia8006566](https://archive.org/details/78_rhythm-time-records-album-1_elizabeth-l-sehon-emma-lou-obrien_gbia8006566) | 814 | train |
| [78_romance-op78-no2_asti-francesco-gteborgs-symfoniorkester](https://archive.org/details/78_romance-op78-no2_asti-francesco-gteborgs-symfoniorkester) | 16 | train |
| [78_sakrat-elomr_george-farah_gbia0393208b](https://archive.org/details/78_sakrat-elomr_george-farah_gbia0393208b) | 714 | train |
| [78_the-clouds-will-soon-roll-by_louis-hardy_2024_wave](https://archive.org/details/78_the-clouds-will-soon-roll-by_louis-hardy_2024_wave) | 2000 | train |
| [78_the-islander_dudley-roy_gbia3041188a](https://archive.org/details/78_the-islander_dudley-roy_gbia3041188a) | 334 | test |
| [78_the-simple-simon-party_billy-murray-montgomery_gbia0277193b](https://archive.org/details/78_the-simple-simon-party_billy-murray-montgomery_gbia0277193b) | 820 | train |
| [78_the-st-louis-blues_ferera-and-paaluhi-w-c-handy_gbia0264780a](https://archive.org/details/78_the-st-louis-blues_ferera-and-paaluhi-w-c-handy_gbia0264780a) | 536 | train |
| [78_the-stars-and-stripes-forever-march_imperial-marimba-band-j-p-sousa_gbia0549589a](https://archive.org/details/78_the-stars-and-stripes-forever-march_imperial-marimba-band-j-p-sousa_gbia0549589a) | 1798 | train |
| [78_the-virgins-slumber-song_julia-culp-coenraad-v-bos-mari-wiegenlied-max-reger-ed_gbia3012107a](https://archive.org/details/78_the-virgins-slumber-song_julia-culp-coenraad-v-bos-mari-wiegenlied-max-reger-ed_gbia3012107a) | 81 | train |
| [78_therell-be-some-changes-made-la-cosa-cambiar_moulin-rouge-orchestra-higgins-ove_gbia0404623b](https://archive.org/details/78_therell-be-some-changes-made-la-cosa-cambiar_moulin-rouge-orchestra-higgins-ove_gbia0404623b) | 273 | train |
| [78_therell-be-some-changes-made_lloyd-sullivan-herb-kern_gbia0484442a](https://archive.org/details/78_therell-be-some-changes-made_lloyd-sullivan-herb-kern_gbia0484442a) | 13 | train |
| [78_they-needed-a-song-bird-in-heaven-so-god-took-caruso-away_sam-ash-brown-little-sta_gbia0400086a](https://archive.org/details/78_they-needed-a-song-bird-in-heaven-so-god-took-caruso-away_sam-ash-brown-little-sta_gbia0400086a) | 531 | train |
| [78_til-dig-hymne-lamour_raquel-rastenni-harry-felberts-sekstet-mogens-dam-marguer_gbia0125594b](https://archive.org/details/78_til-dig-hymne-lamour_raquel-rastenni-harry-felberts-sekstet-mogens-dam-marguer_gbia0125594b) | 2000 | train |
| [78_tis-wonderful-to-me_blackwood-bros-quartet_gbia0450270b](https://archive.org/details/78_tis-wonderful-to-me_blackwood-bros-quartet_gbia0450270b) | 546 | train |
| [78_title-in-hindustani_jagmohan-sursagar-hasrat-jaipuri_gbia0076800a](https://archive.org/details/78_title-in-hindustani_jagmohan-sursagar-hasrat-jaipuri_gbia0076800a) | 370 | train |
| [78_tnk-p-de-gode-ting-love-is-a-golden-ring_raquel-rastenni-harry-felberts-orkeste_gbia7009158a](https://archive.org/details/78_tnk-p-de-gode-ting-love-is-a-golden-ring_raquel-rastenni-harry-felberts-orkeste_gbia7009158a) | 1308 | train |
| [78_together_einar-bjrneboe-irving-berlin_gbia7016691a](https://archive.org/details/78_together_einar-bjrneboe-irving-berlin_gbia7016691a) | 1307 | train |
| [78_together_paul-whiteman-his-concert-orch-de-sylva-brown-henderson_gbia7002607b](https://archive.org/details/78_together_paul-whiteman-his-concert-orch-de-sylva-brown-henderson_gbia7002607b) | 960 | train |
| [78_toi-qui-disais-qui-disais-qui-disais-the-girl-without-a-name_tony-proteau-et-son_gbia0485066a](https://archive.org/details/78_toi-qui-disais-qui-disais-qui-disais-the-girl-without-a-name_tony-proteau-et-son_gbia0485066a) | 744 | test |
| [78_tom-cat-boogie_johnnie-lee-wills-and-his-boys-leon-huff-mayo-wills_gbia0259857b](https://archive.org/details/78_tom-cat-boogie_johnnie-lee-wills-and-his-boys-leon-huff-mayo-wills_gbia0259857b) | 376 | train |
| [78_ton-image-est-dans-mon-coeur-always-in-my-heart_eddie-checkler-and-his-continenta_gbia7034867a](https://archive.org/details/78_ton-image-est-dans-mon-coeur-always-in-my-heart_eddie-checkler-and-his-continenta_gbia7034867a) | 104 | train |
| [78_too-old-to-cut-the-mustard_ann-jones-ann-jones-and-the-boys-bill-carlisle_gbia0425420b](https://archive.org/details/78_too-old-to-cut-the-mustard_ann-jones-ann-jones-and-the-boys-bill-carlisle_gbia0425420b) | 337 | train |
| [78_tootle_pat-omalley-wilder-barer-mitchell-miller_gbia0534630a](https://archive.org/details/78_tootle_pat-omalley-wilder-barer-mitchell-miller_gbia0534630a) | 1031 | test |
| [78_tosca-recondita-armonia-strange-harmony-act-1_giovanni-martinelli-puccini_gbia0297004b](https://archive.org/details/78_tosca-recondita-armonia-strange-harmony-act-1_giovanni-martinelli-puccini_gbia0297004b) | 349 | train |
| [78_trafalgar_the-royal-horse-guards-band_gbia3013922b](https://archive.org/details/78_trafalgar_the-royal-horse-guards-band_gbia3013922b) | 990 | train |
| [78_tristesse-etude-e-dur_kai-mortensens-strygeorkester-chopin_gbia7033719b](https://archive.org/details/78_tristesse-etude-e-dur_kai-mortensens-strygeorkester-chopin_gbia7033719b) | 555 | train |
| [78_tristesse_mario-melfi-and-his-tango-orchestra_wave](https://archive.org/details/78_tristesse_mario-melfi-and-his-tango-orchestra_wave) | 2000 | test |
| [78_tro-lille-hjerte-line_raquel-rastenni-harry-felberts-sekstet-b-linz-francis-lope_gbia0125804a](https://archive.org/details/78_tro-lille-hjerte-line_raquel-rastenni-harry-felberts-sekstet-b-linz-francis-lope_gbia0125804a) | 872 | train |
| [78_trois-fois-merci_emil-stern-et-son-orchestre-de-danse-michel-emer-y-pierce-corsey_gbia0367836a](https://archive.org/details/78_trois-fois-merci_emil-stern-et-son-orchestre-de-danse-michel-emer-y-pierce-corsey_gbia0367836a) | 752 | train |
| [78_true-blues_milt-jackson-quartet-milt-jackson-percy-heath-john-lewis-kenny-clarke_gbia0160451b](https://archive.org/details/78_true-blues_milt-jackson-quartet-milt-jackson-percy-heath-john-lewis-kenny-clarke_gbia0160451b) | 417 | train |
| [78_try-to-forget_savannah-churchill-ralph-hermanns-orchestra-safier-hermann-hershey_gbia0039633b](https://archive.org/details/78_try-to-forget_savannah-churchill-ralph-hermanns-orchestra-safier-hermann-hershey_gbia0039633b) | 531 | train |
| [78_try-to-smile_carl-henry-orchestra_gbia0202078b](https://archive.org/details/78_try-to-smile_carl-henry-orchestra_gbia0202078b) | 1357 | train |
| [78_tuli-tuli-tulipanene-tu-li-tuliptime_nora-brockstedt-og-oddvar-sanne-maria-grever_gbia7023613a](https://archive.org/details/78_tuli-tuli-tulipanene-tu-li-tuliptime_nora-brockstedt-og-oddvar-sanne-maria-grever_gbia7023613a) | 269 | train |
| [78_twilight-song_bobby-doyle-ray-bloch-and-his-orchestra-lawrence-drutman_gbia0206867a](https://archive.org/details/78_twilight-song_bobby-doyle-ray-bloch-and-his-orchestra-lawrence-drutman_gbia0206867a) | 151 | train |
| [78_twin-guitar-boogie_leon-mcauliffe-and-his-western-swing-band-mcauliffe-shamblin_gbia0068949a](https://archive.org/details/78_twin-guitar-boogie_leon-mcauliffe-and-his-western-swing-band-mcauliffe-shamblin_gbia0068949a) | 993 | train |
| [78_twinkle-twinkle-little-star-the-bus_gbia8004377](https://archive.org/details/78_twinkle-twinkle-little-star-the-bus_gbia8004377) | 230 | train |
| [78_un-homme-est-un-homme_hubert-rostaing-et-son-orchestre-oscar-brand_gbia0437089b](https://archive.org/details/78_un-homme-est-un-homme_hubert-rostaing-et-son-orchestre-oscar-brand_gbia0437089b) | 550 | test |
| [78_un-inconnu-trappe-a-la-porte_jacqueline-valois-m-cab-s-weber-guy-lafarge-dandr_gbia0431830b](https://archive.org/details/78_un-inconnu-trappe-a-la-porte_jacqueline-valois-m-cab-s-weber-guy-lafarge-dandr_gbia0431830b) | 198 | train |
| [78_un-petit-bout-de-satin_henri-rossotti-et-son-orchestre-tropical-l-ferrari-j-plant_gbia0376836a](https://archive.org/details/78_un-petit-bout-de-satin_henri-rossotti-et-son-orchestre-tropical-l-ferrari-j-plant_gbia0376836a) | 174 | train |
| [78_una-voce-poco-fa_miss-elizabeth-newbold-rossini_gbia3042259b](https://archive.org/details/78_una-voce-poco-fa_miss-elizabeth-newbold-rossini_gbia3042259b) | 544 | train |
| [78_uncles-quit-work-too_bob-roberts_gbia0313682a](https://archive.org/details/78_uncles-quit-work-too_bob-roberts_gbia0313682a) | 761 | train |
| [78_underneath-the-arches_just-an-echo-in-the-valley_by-the-fireside_phil-green-ahb_30jul-2020_wave](https://archive.org/details/78_underneath-the-arches_just-an-echo-in-the-valley_by-the-fireside_phil-green-ahb_30jul-2020_wave) | 2000 | train |
| [78_une-nuit-dans-tes-bras_raphael-biondi-og-hans-tangoorkester-jean-raphael-michel-eme_gbia7010450b](https://archive.org/details/78_une-nuit-dans-tes-bras_raphael-biondi-og-hans-tangoorkester-jean-raphael-michel-eme_gbia7010450b) | 1685 | train |
| [78_until_teschemacher-sanderson_gbia0018203b](https://archive.org/details/78_until_teschemacher-sanderson_gbia0018203b) | 453 | train |
| [78_untiy-polka_ray-henry-and-his-orchestra-untia-p.-r.-h._gbia0002143a](https://archive.org/details/78_untiy-polka_ray-henry-and-his-orchestra-untia-p.-r.-h._gbia0002143a) | 296 | train |
| [78_up-in-my-heavenly-home_charles-watkins-w-bell_gbia0101846a](https://archive.org/details/78_up-in-my-heavenly-home_charles-watkins-w-bell_gbia0101846a) | 1224 | train |
| [78_uptown-blues-haunted-town_charlie-barnet-and-his-orchestra-lena-horne-lunceford-fo_gbia0382477a](https://archive.org/details/78_uptown-blues-haunted-town_charlie-barnet-and-his-orchestra-lena-horne-lunceford-fo_gbia0382477a) | 88 | train |
| [78_valencia_savoy-havana-band-jos-padilla_gbia7017576a](https://archive.org/details/78_valencia_savoy-havana-band-jos-padilla_gbia7017576a) | 1135 | train |
| [78_valley-of-birds-underwater-world_the-westway-studio-orchestra-k-palmer-r-hanmer_gbia3003511b](https://archive.org/details/78_valley-of-birds-underwater-world_the-westway-studio-orchestra-k-palmer-r-hanmer_gbia3003511b) | 279 | train |
| [78_vals-i-tollare_accordion-clubs-store-harmonikaorkester-hans-erik-ns_gbia7007358b](https://archive.org/details/78_vals-i-tollare_accordion-clubs-store-harmonikaorkester-hans-erik-ns_gbia7007358b) | 416 | train |
| [78_valse-erica-walec-eryka_orkiestra-polonii_gbia0454595a](https://archive.org/details/78_valse-erica-walec-eryka_orkiestra-polonii_gbia0454595a) | 1608 | train |
| [78_vanished-army_band-of-the-welsh-guards-kenneth-alford_gbia0059564a](https://archive.org/details/78_vanished-army_band-of-the-welsh-guards-kenneth-alford_gbia0059564a) | 1218 | train |
| [78_vanity_phil-reed-manus-bierman-wood_gbia0463030a](https://archive.org/details/78_vanity_phil-reed-manus-bierman-wood_gbia0463030a) | 342 | train |
| [78_varcarola-triste_beniamino-gigli-banderano-cecconi-vito-carnevali_gbia0484278a](https://archive.org/details/78_varcarola-triste_beniamino-gigli-banderano-cecconi-vito-carnevali_gbia0484278a) | 559 | train |
| [78_vaughn-monroe-show-part-2_vaughn-monroe_gbia0566265b](https://archive.org/details/78_vaughn-monroe-show-part-2_vaughn-monroe_gbia0566265b) | 317 | train |
| [78_vecchio-varieta-old-vaudeville_f-ferrari-strappini_gbia0505020a](https://archive.org/details/78_vecchio-varieta-old-vaudeville_f-ferrari-strappini_gbia0505020a) | 545 | train |
| [78_ved-kajen_lulu-ziegler-henrik-blichmanns-ensemble-h-blichmann-h-kjrulff-schmidt_gbia0125342a](https://archive.org/details/78_ved-kajen_lulu-ziegler-henrik-blichmanns-ensemble-h-blichmann-h-kjrulff-schmidt_gbia0125342a) | 2000 | train |
| [78_venezia_neues-philharm-blser-orchester-1950-g-fabian-hanns-steinkopf_gbia0184979a](https://archive.org/details/78_venezia_neues-philharm-blser-orchester-1950-g-fabian-hanns-steinkopf_gbia0184979a) | 277 | train |
| [78_vera-jsem-t-ekala_r-a-dvorsky-se-svm-orchestrem-a-sbor-vclava-bhy_gbia0420813b](https://archive.org/details/78_vera-jsem-t-ekala_r-a-dvorsky-se-svm-orchestrem-a-sbor-vclava-bhy_gbia0420813b) | 295 | train |
| [78_vereinte-veteranen-marsch-von-feige_kaiser-franz-garde-gren-regt-kgl-kapellmeis_gbia0123617a](https://archive.org/details/78_vereinte-veteranen-marsch-von-feige_kaiser-franz-garde-gren-regt-kgl-kapellmeis_gbia0123617a) | 97 | train |
| [78_vet-du-vad-jag-nskar-mej-fdelsedagen_max-hansen-jens-warnys-orkester-kai-norma_gbia7005417b](https://archive.org/details/78_vet-du-vad-jag-nskar-mej-fdelsedagen_max-hansen-jens-warnys-orkester-kai-norma_gbia7005417b) | 2000 | train |
| [78_vetci-ludia-povedaj-e-ja-lbim-mlynrku_ludo-bitt-so-svojou-cignskou-kapel_gbia0183669b](https://archive.org/details/78_vetci-ludia-povedaj-e-ja-lbim-mlynrku_ludo-bitt-so-svojou-cignskou-kapel_gbia0183669b) | 669 | train |
| [78_victory-industrial-project_wilfred-burns_gbia3025326b](https://archive.org/details/78_victory-industrial-project_wilfred-burns_gbia3025326b) | 378 | train |
| [78_vien-leonora-a-piedi-tuoi_mattia-battistini-donizetti_gbia7003885a](https://archive.org/details/78_vien-leonora-a-piedi-tuoi_mattia-battistini-donizetti_gbia7003885a) | 379 | train |
| [78_vienleonora_127_03](https://archive.org/details/78_vienleonora_127_03) | 675 | train |
| [78_vienna-blood_concert-orchestra-johann-strauss_gbia0327886a](https://archive.org/details/78_vienna-blood_concert-orchestra-johann-strauss_gbia0327886a) | 1045 | train |
| [78_viennese-march_carl-ledel-and-his-alpine-troubadors_gbia0507161a](https://archive.org/details/78_viennese-march_carl-ledel-and-his-alpine-troubadors_gbia0507161a) | 78 | train |
| [78_vitamin-polka_the-melody-riders-j-lieb_gbia0527628a](https://archive.org/details/78_vitamin-polka_the-melody-riders-j-lieb_gbia0527628a) | 106 | train |
| [78_vito_rio-grande-tango-band-s-lopez_gbia7000711b](https://archive.org/details/78_vito_rio-grande-tango-band-s-lopez_gbia7000711b) | 355 | train |
| [78_voceenotte_131_12](https://archive.org/details/78_voceenotte_131_12) | 210 | train |
| [78_volkslieder-potpourri-2-teil_joe-alex-mit-seinen-solisten_gbia7035709b](https://archive.org/details/78_volkslieder-potpourri-2-teil_joe-alex-mit-seinen-solisten_gbia7035709b) | 389 | train |
| [78_vom-rhein-der-wein-kling-kling-goldner-wein_herbert-ernst-groh-herm-brandt-m-rhode_gbia3021597b](https://archive.org/details/78_vom-rhein-der-wein-kling-kling-goldner-wein_herbert-ernst-groh-herm-brandt-m-rhode_gbia3021597b) | 2000 | train |
| [78_voot-nay-on-the-vot-nay_the-basin-street-boys-eddie-beals-fourtet-gene-price-orman_gbia0053688a](https://archive.org/details/78_voot-nay-on-the-vot-nay_the-basin-street-boys-eddie-beals-fourtet-gene-price-orman_gbia0053688a) | 722 | train |
| [78_vor-meinem-vaterhaus-steht-eine-linde_r-stolz_gbia0184964a](https://archive.org/details/78_vor-meinem-vaterhaus-steht-eine-linde_r-stolz_gbia0184964a) | 1645 | train |
| [78_voyezsurcetteroche_185_07](https://archive.org/details/78_voyezsurcetteroche_185_07) | 267 | train |
| [78_wagon-wheel_ben-christian-and-his-texas-cowboys-bill-rose_gbia0509994b](https://archive.org/details/78_wagon-wheel_ben-christian-and-his-texas-cowboys-bill-rose_gbia0509994b) | 296 | train |
| [78_waiting-for-the-robert-e-lee_dean-hudson-and-his-orchestra-the-sherry-sisters-muir_gbia0018028a](https://archive.org/details/78_waiting-for-the-robert-e-lee_dean-hudson-and-his-orchestra-the-sherry-sisters-muir_gbia0018028a) | 210 | train |
| [78_waiting-for-the-sun-to-come-out_cleartone-trio-francis-gershwin_gbia0177502b](https://archive.org/details/78_waiting-for-the-sun-to-come-out_cleartone-trio-francis-gershwin_gbia0177502b) | 483 | train |
| [78_waldteufel-memories_de-groot-and-his-orchestra-waldteufel-finck_gbia7001953a](https://archive.org/details/78_waldteufel-memories_de-groot-and-his-orchestra-waldteufel-finck_gbia7001953a) | 791 | test |
| [78_walking-my-blues-away_gatemouth-moore-budd-johnsons-all-stars-budd-johnson-harr_gbia0072604b](https://archive.org/details/78_walking-my-blues-away_gatemouth-moore-budd-johnsons-all-stars-budd-johnson-harr_gbia0072604b) | 538 | train |
| [78_wallaby-walk_the-roundabouts_gbia0024668](https://archive.org/details/78_wallaby-walk_the-roundabouts_gbia0024668) | 211 | train |
| [78_walter-winchell-oct-7-1945_walter-winchell_gbia0281438b](https://archive.org/details/78_walter-winchell-oct-7-1945_walter-winchell_gbia0281438b) | 1319 | train |
| [78_waltz-carousel_schroeders-playboys_gbia0024577a](https://archive.org/details/78_waltz-carousel_schroeders-playboys_gbia0024577a) | 401 | train |
| [78_waltzing-cat_sidney-torch-and-his-orchestra-anderson_gbia7031605b](https://archive.org/details/78_waltzing-cat_sidney-torch-and-his-orchestra-anderson_gbia7031605b) | 460 | train |
| [78_waltzing-to-jimmy-shand-part-2_jimmy-shand-his-band_gbia3021739b](https://archive.org/details/78_waltzing-to-jimmy-shand-part-2_jimmy-shand-his-band_gbia3021739b) | 437 | train |
| [78_war-and-peace_vic-damone-david-terry-his-orch-stone-rota_gbia3025705a](https://archive.org/details/78_war-and-peace_vic-damone-david-terry-his-orch-stone-rota_gbia3025705a) | 121 | train |
| [78_warsaw-concerto_royal-viennese-symphonic-orchestra-richard-addinsell_gbia0195848c](https://archive.org/details/78_warsaw-concerto_royal-viennese-symphonic-orchestra-richard-addinsell_gbia0195848c) | 93 | train |
| [78_warsaw-concerto_royal-viennese-symphonic-orchestra-saint-saens_gbia8002131](https://archive.org/details/78_warsaw-concerto_royal-viennese-symphonic-orchestra-saint-saens_gbia8002131) | 426 | train |
| [78_watcha-gonna-do-now-new-green-light_cliff-johnson-the-harmony-boys_gbia0541724a](https://archive.org/details/78_watcha-gonna-do-now-new-green-light_cliff-johnson-the-harmony-boys_gbia0541724a) | 230 | train |
| [78_watertank-blues-hambone-hollow-my-heart-will-tell-you_the-grosvenor-studio-orches_gbia3009817a](https://archive.org/details/78_watertank-blues-hambone-hollow-my-heart-will-tell-you_the-grosvenor-studio-orches_gbia3009817a) | 113 | train |
| [78_weary-day_delmore-brothers-king-neeley_gbia0224147a](https://archive.org/details/78_weary-day_delmore-brothers-king-neeley_gbia0224147a) | 552 | train |
| [78_weary-way-blues_claude-luter-et-ses-lorientais-hugues-panassie-ida-cox-lovie-austin_gbia0003973b](https://archive.org/details/78_weary-way-blues_claude-luter-et-ses-lorientais-hugues-panassie-ida-cox-lovie-austin_gbia0003973b) | 149 | train |
| [78_wedding-waltz_gene-wisniewski-and-his-harmony-bells-orchestra-and-the-wayfarers-cas_gbia0243894b](https://archive.org/details/78_wedding-waltz_gene-wisniewski-and-his-harmony-bells-orchestra-and-the-wayfarers-cas_gbia0243894b) | 224 | train |
| [78_wenn-die-soldaten-durch-die-stadt-marschieren_regensburger-domchor-die-domspatzen_gbia7000496b](https://archive.org/details/78_wenn-die-soldaten-durch-die-stadt-marschieren_regensburger-domchor-die-domspatzen_gbia7000496b) | 1022 | train |
| [78_wenn-du-mal-heimweh-hast_annemarie-gutwell-das-orchester-karl-loube-hans-korten_gbia7037801b](https://archive.org/details/78_wenn-du-mal-heimweh-hast_annemarie-gutwell-das-orchester-karl-loube-hans-korten_gbia7037801b) | 2000 | train |
| [78_what-are-we-goin-to-do-when-theres-nothing-to-do-on-sunday_arthur-fields-pease_gbia0170597b](https://archive.org/details/78_what-are-we-goin-to-do-when-theres-nothing-to-do-on-sunday_arthur-fields-pease_gbia0170597b) | 1001 | train |
| [78_what-goes-up-must-come-down-and-baby-youve-been-flying-too-high_harry-roy-his-orche_gbia7038798b](https://archive.org/details/78_what-goes-up-must-come-down-and-baby-youve-been-flying-too-high_harry-roy-his-orche_gbia7038798b) | 230 | test |
| [78_what-the-christian-believes-111-sg_gbia3041796a](https://archive.org/details/78_what-the-christian-believes-111-sg_gbia3041796a) | 175 | train |
| [78_what-would-you-like-to-be_gbia0534316a](https://archive.org/details/78_what-would-you-like-to-be_gbia0534316a) | 251 | test |
| [78_whatll-i-do_sam-lanins-dance-orchestra-irving-berlin_gbia0473160a](https://archive.org/details/78_whatll-i-do_sam-lanins-dance-orchestra-irving-berlin_gbia0473160a) | 416 | train |
| [78_wheel-of-fortune_jimmy-thomason-jimmy-thomason-benjamin-weiss_gbia3018032b](https://archive.org/details/78_wheel-of-fortune_jimmy-thomason-jimmy-thomason-benjamin-weiss_gbia3018032b) | 351 | train |
| [78_when-banana-skins-are-falling-ill-come-sliding-back-to-you](https://archive.org/details/78_when-banana-skins-are-falling-ill-come-sliding-back-to-you) | 98 | train |
| [78_when-dixie-stars-are-playing-peek-a-boo_dixie-trio-robinson-bernard_gbia0118742b](https://archive.org/details/78_when-dixie-stars-are-playing-peek-a-boo_dixie-trio-robinson-bernard_gbia0118742b) | 941 | train |
| [78_when-god-is-near_david-taylor-loeen-bushman-a-k-ackley_gbia0535092b](https://archive.org/details/78_when-god-is-near_david-taylor-loeen-bushman-a-k-ackley_gbia0535092b) | 384 | train |
| [78_when-hands-meet_the-zonophone-concert-quartet_gbia3037900b](https://archive.org/details/78_when-hands-meet_the-zonophone-concert-quartet_gbia3037900b) | 278 | train |
| [78_when-he-blest-my-soul_the-green-trio_gbia0394443a](https://archive.org/details/78_when-he-blest-my-soul_the-green-trio_gbia0394443a) | 397 | train |
| [78_when-i-fall-in-love_les-welch-and-his-orchestra-pamela-jopson-e-heyman-victor-young_gbia3015135b](https://archive.org/details/78_when-i-fall-in-love_les-welch-and-his-orchestra-pamela-jopson-e-heyman-victor-young_gbia3015135b) | 24 | train |
| [78_when-i-gave-you-my-love_charlie-gore-and-ruby-wright-charlie-gore-and-ruby-wright-g_gbia0437749b](https://archive.org/details/78_when-i-gave-you-my-love_charlie-gore-and-ruby-wright-charlie-gore-and-ruby-wright-g_gbia0437749b) | 83 | train |
| [78_when-i-grow-up_tom-glazer-charity-bailey-hendl-abrashkin_gbia8003311](https://archive.org/details/78_when-i-grow-up_tom-glazer-charity-bailey-hendl-abrashkin_gbia8003311) | 753 | train |
| [78_when-i-hold-a-bit-of-heaven_jack-day-santa-fe-rangers-kitty-schofer-jimmy-deknight_gbia0094724a](https://archive.org/details/78_when-i-hold-a-bit-of-heaven_jack-day-santa-fe-rangers-kitty-schofer-jimmy-deknight_gbia0094724a) | 50 | train |
| [78_when-i-kiss-my-baby-good-night_robert-carr-sam-mayo_gbia3015881b](https://archive.org/details/78_when-i-kiss-my-baby-good-night_robert-carr-sam-mayo_gbia3015881b) | 1169 | train |
| [78_when-i-survey-the-wondrous-cross_mark-andrews-e-miller_gbia3031666b](https://archive.org/details/78_when-i-survey-the-wondrous-cross_mark-andrews-e-miller_gbia3031666b) | 1095 | train |
| [78_when-its-sleepy-time-down-south_buddy-baker-aho](https://archive.org/details/78_when-its-sleepy-time-down-south_buddy-baker-aho) | 398 | train |
| [78_when-my-baby-smiles-at-me_frank-messina-and-the-mavericks-munro-sterling-lewis_gbia0513722a](https://archive.org/details/78_when-my-baby-smiles-at-me_frank-messina-and-the-mavericks-munro-sterling-lewis_gbia0513722a) | 28 | train |
| [78_when-my-blue-moon-turns-to-gold-again_skeets-yaney-and-the-ozark-cahmpions-walker_gbia0005071a](https://archive.org/details/78_when-my-blue-moon-turns-to-gold-again_skeets-yaney-and-the-ozark-cahmpions-walker_gbia0005071a) | 13 | train |
| [78_when-shadows-fall_the-ambassador-string-orchestra-dolin_gbia0041547a](https://archive.org/details/78_when-shadows-fall_the-ambassador-string-orchestra-dolin_gbia0041547a) | 324 | train |
| [78_when-the-bloom-is-on-the-sage_jesse-rogers-howard-vincent_gbia0424622a](https://archive.org/details/78_when-the-bloom-is-on-the-sage_jesse-rogers-howard-vincent_gbia0424622a) | 1445 | train |
| [78_when-the-honeymoon-was-over_sam-ash-fred-fisher_gbia3015848b](https://archive.org/details/78_when-the-honeymoon-was-over_sam-ash-fred-fisher_gbia3015848b) | 745 | train |
| [78_when-the-leaves-bid-the-trees-goodbye_victor-silvester-and-his-ballroom-orchestra-s_gbia0371720b](https://archive.org/details/78_when-the-leaves-bid-the-trees-goodbye_victor-silvester-and-his-ballroom-orchestra-s_gbia0371720b) | 601 | train |
| [78_when-the-leaves-come-tumbling-down_clyde-doerr-and-his-orchestra-richard-howard_gbia3033383b](https://archive.org/details/78_when-the-leaves-come-tumbling-down_clyde-doerr-and-his-orchestra-richard-howard_gbia3033383b) | 337 | train |
| [78_when-the-leaves-come-tumbling-down_nathan-glantz-orch-richard-howard_gbia0476395b](https://archive.org/details/78_when-the-leaves-come-tumbling-down_nathan-glantz-orch-richard-howard_gbia0476395b) | 476 | train |
| [78_when-the-saints-go-marching-in_celestins-tuxedo-jazz-band-oscar-celestin-bill-ma_gbia0182348a](https://archive.org/details/78_when-the-saints-go-marching-in_celestins-tuxedo-jazz-band-oscar-celestin-bill-ma_gbia0182348a) | 8 | test |
| [78_when-the-ships-come-home_helen-clark-jerome-kern_gbia0083300a](https://archive.org/details/78_when-the-ships-come-home_helen-clark-jerome-kern_gbia0083300a) | 390 | train |
| [78_when-you-and-i-were-young-maggie_criterion-quartet-g-w-johnson-j-a-butterfield_gbia0164665b](https://archive.org/details/78_when-you-and-i-were-young-maggie_criterion-quartet-g-w-johnson-j-a-butterfield_gbia0164665b) | 1974 | train |
| [78_when-you-look-in-the-heart-of-a-rose-the-better-ole_edward-allen-florence-methve_gbia0275303b](https://archive.org/details/78_when-you-look-in-the-heart-of-a-rose-the-better-ole_edward-allen-florence-methve_gbia0275303b) | 207 | train |
| [78_where-did-robinson-go-with-friday-on-a-saturday-night](https://archive.org/details/78_where-did-robinson-go-with-friday-on-a-saturday-night) | 487 | test |
| [78_where-the-bamboo-babies-grow_hazay-natzys-orchestra-donaldson_gbia0298042b](https://archive.org/details/78_where-the-bamboo-babies-grow_hazay-natzys-orchestra-donaldson_gbia0298042b) | 399 | train |
| [78_where-the-bamboo-babies-grow_hazy-natzy-and-his-orchestra-donaldson-jack-green_gbia0436979b](https://archive.org/details/78_where-the-bamboo-babies-grow_hazy-natzy-and-his-orchestra-donaldson-jack-green_gbia0436979b) | 470 | train |
| [78_where-the-lazy-daisies-grow_ernest-hare-cliff-friend_gbia0426916b](https://archive.org/details/78_where-the-lazy-daisies-grow_ernest-hare-cliff-friend_gbia0426916b) | 497 | train |
| [78_whered-you-get-those-eyes_macy-and-smalle-the-radio-aces-walter-donaldson_gbia0527432a](https://archive.org/details/78_whered-you-get-those-eyes_macy-and-smalle-the-radio-aces-walter-donaldson_gbia0527432a) | 2000 | train |
| [78_while-my-lady-sleeps_bob-morris-jack-fascinato-quartet-jack-fascinato-george-barnes_gbia0394842a](https://archive.org/details/78_while-my-lady-sleeps_bob-morris-jack-fascinato-quartet-jack-fascinato-george-barnes_gbia0394842a) | 1945 | train |
| [78_whispering-of-the-flowers_alonzo-and-his-orchestra-von-blon_gbia0538451b](https://archive.org/details/78_whispering-of-the-flowers_alonzo-and-his-orchestra-von-blon_gbia0538451b) | 1323 | train |
| [78_whispering-wheat_paul-franklin-his-orchestra-peter-knight_gbia3008507a](https://archive.org/details/78_whispering-wheat_paul-franklin-his-orchestra-peter-knight_gbia3008507a) | 1126 | train |
| [78_white-christmas_bob-harvey-and-his-orchestra-art-juhlin-irving-berlin_gbia0203811a](https://archive.org/details/78_white-christmas_bob-harvey-and-his-orchestra-art-juhlin-irving-berlin_gbia0203811a) | 302 | train |
| [78_white-wings_will-oakland-winter_gbia3037138a](https://archive.org/details/78_white-wings_will-oakland-winter_gbia3037138a) | 443 | train |
| [78_whitherwhitherhaveyougone_030_06](https://archive.org/details/78_whitherwhitherhaveyougone_030_06) | 286 | train |
| [78_who-believed-in-you_california-ramblers-anatol-friedland_gbia0464619b](https://archive.org/details/78_who-believed-in-you_california-ramblers-anatol-friedland_gbia0464619b) | 308 | train |
| [78_who-me-if-you-dont-talk-too-much_riley-shepard-the-thomas-family-riley-shepard_gbia0263017b](https://archive.org/details/78_who-me-if-you-dont-talk-too-much_riley-shepard-the-thomas-family-riley-shepard_gbia0263017b) | 872 | train |
| [78_who_international-dance-orchestra-kerns_gbia0448049a](https://archive.org/details/78_who_international-dance-orchestra-kerns_gbia0448049a) | 532 | train |
| [78_whose-izzy-is-he-is-he-yours-or-is-he-mine_harry-blake-brown-green-sturm_gbia0329803b](https://archive.org/details/78_whose-izzy-is-he-is-he-yours-or-is-he-mine_harry-blake-brown-green-sturm_gbia0329803b) | 934 | train |
| [78_whose-izzy-is-he_clarkson-rose-green-sturm_gbia3040943b](https://archive.org/details/78_whose-izzy-is-he_clarkson-rose-green-sturm_gbia3040943b) | 759 | train |
| [78_why-dont-you-practice-what-you-preach_gerry-moore-sigler-goodhart-hoffman-victor_gbia3007676a](https://archive.org/details/78_why-dont-you-practice-what-you-preach_gerry-moore-sigler-goodhart-hoffman-victor_gbia3007676a) | 1727 | train |
| [78_why-should-i-cry-over-you_lane-dales-marimba-band-miller-cohn_gbia0118719b](https://archive.org/details/78_why-should-i-cry-over-you_lane-dales-marimba-band-miller-cohn_gbia0118719b) | 668 | train |
| [78_wiazanka-ukrainskih-narodnih-pisen-potpourri-of-ukrainian-folk-songs_ukrainian-band_gbia3028317b](https://archive.org/details/78_wiazanka-ukrainskih-narodnih-pisen-potpourri-of-ukrainian-folk-songs_ukrainian-band_gbia3028317b) | 375 | train |
| [78_wiegenlied-cradle-song_ilona-klenk-brahms-o-weiss_gbia3009773a](https://archive.org/details/78_wiegenlied-cradle-song_ilona-klenk-brahms-o-weiss_gbia3009773a) | 1404 | train |
| [78_wiegenlied-im-sommer_tiana-lemnitz-michael-raucheisen-rob-reinick-hugo-wolf_gbia0551498b](https://archive.org/details/78_wiegenlied-im-sommer_tiana-lemnitz-michael-raucheisen-rob-reinick-hugo-wolf_gbia0551498b) | 2000 | train |
| [78_wiegenlied_laider-edi-sigurdsson-haraldur](https://archive.org/details/78_wiegenlied_laider-edi-sigurdsson-haraldur) | 1 | train |
| [78_wiegenlied_lotte-leonard-dr-felix-gnther-weber_gbia0254153b](https://archive.org/details/78_wiegenlied_lotte-leonard-dr-felix-gnther-weber_gbia0254153b) | 675 | train |
| [78_wiener-blut_franz-mihalovic-und-sein-walzer-orchester-johann-strauss_gbia7037877a](https://archive.org/details/78_wiener-blut_franz-mihalovic-und-sein-walzer-orchester-johann-strauss_gbia7037877a) | 156 | train |
| [78_wiener-blut_marcel-wittrisch-joh-strau-victor-leon-leo-stein-adolf-mller-jun_gbia0197330b](https://archive.org/details/78_wiener-blut_marcel-wittrisch-joh-strau-victor-leon-leo-stein-adolf-mller-jun_gbia0197330b) | 2000 | train |
| [78_wiener-brger_franz-mihalovic-mit-seinem-walzer-orchester-carl-michael-ziehrer_gbia7039391b](https://archive.org/details/78_wiener-brger_franz-mihalovic-mit-seinem-walzer-orchester-carl-michael-ziehrer_gbia7039391b) | 289 | test |
| [78_wiggle-woogie_count-basie-and-his-orch-warren_gbia0121285a](https://archive.org/details/78_wiggle-woogie_count-basie-and-his-orch-warren_gbia0121285a) | 80 | train |
| [78_wild-horses_loren-becker-enoch-light-orchestra-and-chorus-k-c-rogan_gbia0042616b](https://archive.org/details/78_wild-horses_loren-becker-enoch-light-orchestra-and-chorus-k-c-rogan_gbia0042616b) | 169 | train |
| [78_william-tell-resta-immobile-flinch-not-nor-stir-a-limb_giuseppe-de-luca-rossini_gbia0478757a](https://archive.org/details/78_william-tell-resta-immobile-flinch-not-nor-stir-a-limb_giuseppe-de-luca-rossini_gbia0478757a) | 1420 | train |
| [78_william-tell-selva-opaca-deep-shaded-forest_frances-alda-rossini_gbia0446597a](https://archive.org/details/78_william-tell-selva-opaca-deep-shaded-forest_frances-alda-rossini_gbia0446597a) | 248 | train |
| [78_william-tell_orchestra-of-the-opera-comique-g-cloez-rossini_gbia3007496a](https://archive.org/details/78_william-tell_orchestra-of-the-opera-comique-g-cloez-rossini_gbia3007496a) | 686 | train |
| [78_winter-garden-waltz](https://archive.org/details/78_winter-garden-waltz) | 185 | train |
| [78_winter-wonderland_cosmo-teri-smith-bernard_gbia0059611b](https://archive.org/details/78_winter-wonderland_cosmo-teri-smith-bernard_gbia0059611b) | 1141 | train |
| [78_winterland-walt_harmony-kings-polka-band-m.-alberts_gbia0007671a](https://archive.org/details/78_winterland-walt_harmony-kings-polka-band-m.-alberts_gbia0007671a) | 794 | train |
| [78_winterstrme-wichen-dem-wonnemond-winter-storms-have-waned-in-the-moon-of-may-act_gbia0122582a](https://archive.org/details/78_winterstrme-wichen-dem-wonnemond-winter-storms-have-waned-in-the-moon-of-may-act_gbia0122582a) | 2000 | train |
| [78_wishing-and-waiting_johnny-hodges-his-orchestra-johnny-hodges-harold-baker-jimmy_gbia0075471b](https://archive.org/details/78_wishing-and-waiting_johnny-hodges-his-orchestra-johnny-hodges-harold-baker-jimmy_gbia0075471b) | 455 | test |
| [78_with-plenty-of-money-and-you_harry-roy-his-orchestra-dubin-warren_gbia3021908a](https://archive.org/details/78_with-plenty-of-money-and-you_harry-roy-his-orchestra-dubin-warren_gbia3021908a) | 377 | train |
| [78_witness_maceo-woods-singers-maceo-woods_gbia0073249a](https://archive.org/details/78_witness_maceo-woods-singers-maceo-woods_gbia0073249a) | 452 | train |
| [78_wobbly-ice-skater-wobbly-cyclist-stilt-walkers-simple-soul_the-crawford-light-orche_gbia3017533a](https://archive.org/details/78_wobbly-ice-skater-wobbly-cyclist-stilt-walkers-simple-soul_the-crawford-light-orche_gbia3017533a) | 335 | train |
| [78_wohin-soll-ich-gehen_menasha-oppenheim-harry-lubin-quintet-o-strock_gbia0363905a](https://archive.org/details/78_wohin-soll-ich-gehen_menasha-oppenheim-harry-lubin-quintet-o-strock_gbia0363905a) | 76 | train |
| [78_women-screaming_gbia3016957b](https://archive.org/details/78_women-screaming_gbia3016957b) | 2000 | train |
| [78_wont-you-write-a-letter-papa_charles-miller_gbia0083083a](https://archive.org/details/78_wont-you-write-a-letter-papa_charles-miller_gbia0083083a) | 323 | train |
| [78_woodland-flowers-barn-dance_alexander-prince-felix-burns_gbia3034079b](https://archive.org/details/78_woodland-flowers-barn-dance_alexander-prince-felix-burns_gbia3034079b) | 568 | train |
| [78_wopa-polka_w.-jagiello-j.-koldon-lil-wally-the-lucky-harmony-boys-orchestra_gbia0000088b](https://archive.org/details/78_wopa-polka_w.-jagiello-j.-koldon-lil-wally-the-lucky-harmony-boys-orchestra_gbia0000088b) | 27 | train |
| [78_words_maryland-dance-orchestra-otis-spencer_gbia3014436a](https://archive.org/details/78_words_maryland-dance-orchestra-otis-spencer_gbia3014436a) | 580 | train |
| [78_work-in-progress-side-2_the-light-symphonia-roberto-capelli-ray-jones_gbia3025407b](https://archive.org/details/78_work-in-progress-side-2_the-light-symphonia-roberto-capelli-ray-jones_gbia3025407b) | 342 | train |
| [78_workaday-world-horses-for-courses_group-forty-orchestra-jack-beaver-paul-fenoulhet_gbia3013017b](https://archive.org/details/78_workaday-world-horses-for-courses_group-forty-orchestra-jack-beaver-paul-fenoulhet_gbia3013017b) | 658 | train |
| [78_world-champions_group-forty-orchestra-harry-rabinowitz-eric-cook_gbia3013002a](https://archive.org/details/78_world-champions_group-forty-orchestra-harry-rabinowitz-eric-cook_gbia3013002a) | 109 | train |
| [78_worried-over-you_paul-gayten-trio-paul-gayten-warren-staley-edgar-blanchard-rober_gbia0064216b](https://archive.org/details/78_worried-over-you_paul-gayten-trio-paul-gayten-warren-staley-edgar-blanchard-rober_gbia0064216b) | 168 | train |
| [78_write-me-a-letter_the-ravens-howard-biggs_gbia0383878a](https://archive.org/details/78_write-me-a-letter_the-ravens-howard-biggs_gbia0383878a) | 158 | train |
| [78_xxvii-the-last-song-of-the-dawn_the-son-of-bead-chant-singer_gbia0082801j](https://archive.org/details/78_xxvii-the-last-song-of-the-dawn_the-son-of-bead-chant-singer_gbia0082801j) | 19 | train |
| [78_ye-banks-and-braes_charles-draper_gbia3007976b](https://archive.org/details/78_ye-banks-and-braes_charles-draper_gbia3007976b) | 394 | train |
| [78_yearning-just-for-you_billy-wynnes-greenwich-village-inn-orchestra-benny-davis-_gbia0083032a](https://archive.org/details/78_yearning-just-for-you_billy-wynnes-greenwich-village-inn-orchestra-benny-davis-_gbia0083032a) | 1250 | train |
| [78_yellow-tulip_bosworths-dance-orchestra-harry-new_gbia7034961b](https://archive.org/details/78_yellow-tulip_bosworths-dance-orchestra-harry-new_gbia7034961b) | 2000 | train |
| [78_yerevanda-khan_minasian-trio_gbia0285069a](https://archive.org/details/78_yerevanda-khan_minasian-trio_gbia0285069a) | 577 | train |
| [78_yes-yes-in-your-eyes_bunk-johnsons-band_gbia0283450b](https://archive.org/details/78_yes-yes-in-your-eyes_bunk-johnsons-band_gbia0283450b) | 2000 | train |
| [78_yiddle-on-your-fiddle_albert-whelan_gbia0061602b](https://archive.org/details/78_yiddle-on-your-fiddle_albert-whelan_gbia0061602b) | 237 | train |
| [78_yo-quiero-recordarte_orquesta-lazaro-quintero-rafita-martinez-jaime-yamin_gbia0029711a](https://archive.org/details/78_yo-quiero-recordarte_orquesta-lazaro-quintero-rafita-martinez-jaime-yamin_gbia0029711a) | 472 | train |
| [78_you-and-i-tu-y-yo_imperial-dance-orchestra-thompson-archer_gbia3013740a](https://archive.org/details/78_you-and-i-tu-y-yo_imperial-dance-orchestra-thompson-archer_gbia3013740a) | 795 | train |
| [78_you-are-doin-me-me-wrong_arthur-gunter-gunter_gbia0053641b](https://archive.org/details/78_you-are-doin-me-me-wrong_arthur-gunter-gunter_gbia0053641b) | 274 | train |
| [78_you-are-my-sunbeam_frank-emerson_gbia3040818b](https://archive.org/details/78_you-are-my-sunbeam_frank-emerson_gbia3040818b) | 742 | train |
| [78_you-are-my-sunshine_frank-messina-and-the-mavericks-davis-mitchell_gbia0510860a](https://archive.org/details/78_you-are-my-sunshine_frank-messina-and-the-mavericks-davis-mitchell_gbia0510860a) | 65 | train |
| [78_you-call-everybody-darlin_bruce-hayes-trace-martin-watts_gbia0334599a](https://archive.org/details/78_you-call-everybody-darlin_bruce-hayes-trace-martin-watts_gbia0334599a) | 694 | train |
| [78_you-dont-learn-that-in-school_roberta-lee-alfred-fisher-dartega_gbia0061166a](https://archive.org/details/78_you-dont-learn-that-in-school_roberta-lee-alfred-fisher-dartega_gbia0061166a) | 155 | train |
| [78_you-go-well-with-my-heart_the-maumee-valley-boys-howard-rettig-brown-hersh_gbia0388486a](https://archive.org/details/78_you-go-well-with-my-heart_the-maumee-valley-boys-howard-rettig-brown-hersh_gbia0388486a) | 893 | train |
| [78_you-got-evrything-a-sweet-mama-needs-but-me_helen-mcdonald-lemuel-fowler-fowler_gbia0486610b](https://archive.org/details/78_you-got-evrything-a-sweet-mama-needs-but-me_helen-mcdonald-lemuel-fowler-fowler_gbia0486610b) | 723 | test |
| [78_you-gotta-see-baby-tonight-or-you-wont-see-baby-at-all_louis-prima-and-his-orche_gbia0069552a](https://archive.org/details/78_you-gotta-see-baby-tonight-or-you-wont-see-baby-at-all_louis-prima-and-his-orche_gbia0069552a) | 101 | train |
| [78_you-intrigue-me_bernice-parks-fred-normans-orchestra-spielman-neiburg_gbia0005309a](https://archive.org/details/78_you-intrigue-me_bernice-parks-fred-normans-orchestra-spielman-neiburg_gbia0005309a) | 288 | train |
| [78_you-little-fishing-girl_carl-woitschach-waldermann_gbia3015083b](https://archive.org/details/78_you-little-fishing-girl_carl-woitschach-waldermann_gbia3015083b) | 616 | train |
| [78_you-say-its-all-over-now_cliff-carlisle-cliff-carlisle_gbia0501282a](https://archive.org/details/78_you-say-its-all-over-now_cliff-carlisle-cliff-carlisle_gbia0501282a) | 1507 | test |
| [78_youll-find-more-love-in-a-broken-heart_ricky-hale-remo-biondi-orch-sid-prosen-d_gbia0447376b](https://archive.org/details/78_youll-find-more-love-in-a-broken-heart_ricky-hale-remo-biondi-orch-sid-prosen-d_gbia0447376b) | 671 | train |
| [78_your-conscience-tells-you-so_jerry-wald-and-his-orchestra-mary-nash-raye-carter_gbia0093957a](https://archive.org/details/78_your-conscience-tells-you-so_jerry-wald-and-his-orchestra-mary-nash-raye-carter_gbia0093957a) | 116 | train |
| [78_your-mother-still-prays-for-you_gbia0457256b](https://archive.org/details/78_your-mother-still-prays-for-you_gbia0457256b) | 321 | train |
| [78_youre-driving-me-crazy_mel-torme-with-sonny-burke-and-his-orchestra-walter-donald_gbia0027300b](https://archive.org/details/78_youre-driving-me-crazy_mel-torme-with-sonny-burke-and-his-orchestra-walter-donald_gbia0027300b) | 822 | test |
| [78_youre-in-kentucky-sure-as-youre-born_david-harris_gbia0010657a](https://archive.org/details/78_youre-in-kentucky-sure-as-youre-born_david-harris_gbia0010657a) | 332 | train |
| [78_youre-looking-for-romance_eddie-duchin-his-orchestra-neiburg-levinson_gbia7008856a](https://archive.org/details/78_youre-looking-for-romance_eddie-duchin-his-orchestra-neiburg-levinson_gbia7008856a) | 887 | train |
| [78_youre-mine_shirley-gunter-and-the-queens-gunter-taylor_gbia0289961a](https://archive.org/details/78_youre-mine_shirley-gunter-and-the-queens-gunter-taylor_gbia0289961a) | 527 | train |
| [78_youre-my-love-song_ken-griffin_gbia0109181b](https://archive.org/details/78_youre-my-love-song_ken-griffin_gbia0109181b) | 205 | train |
| [78_youre-the-one-in-my-heart_tony-alamo-joe-candullo-his-orch-willmore-nutter_gbia0470351b](https://archive.org/details/78_youre-the-one-in-my-heart_tony-alamo-joe-candullo-his-orch-willmore-nutter_gbia0470351b) | 379 | train |
| [78_youve-got-me-in-the-palm-of-your-hand-me-tienes-en-la-palma-de-las-manos_dick-ro_gbia0100072b](https://archive.org/details/78_youve-got-me-in-the-palm-of-your-hand-me-tienes-en-la-palma-de-las-manos_dick-ro_gbia0100072b) | 257 | train |
| [78_youwere-coming-through-the-corn-molly-dear_ernest-heathley-decapo-orchestra-mellor-_gbia3015364b](https://archive.org/details/78_youwere-coming-through-the-corn-molly-dear_ernest-heathley-decapo-orchestra-mellor-_gbia3015364b) | 135 | train |
| [78_ywllow-roses-theres-poison-in-your-heart-letters-have-no-arms_gbia0086842a](https://archive.org/details/78_ywllow-roses-theres-poison-in-your-heart-letters-have-no-arms_gbia0086842a) | 24 | train |
| [78_zahrajce-mi_juraj-kralik-ludova-kapela-lucnica-juraj-jozsa_gbia0102712b](https://archive.org/details/78_zahrajce-mi_juraj-kralik-ludova-kapela-lucnica-juraj-jozsa_gbia0102712b) | 140 | test |
| [78_zakochana-dziewczyna-the-girl-in-love_frank-wojnarowski-and-his-orchestra_gbia0528117b](https://archive.org/details/78_zakochana-dziewczyna-the-girl-in-love_frank-wojnarowski-and-his-orchestra_gbia0528117b) | 5 | train |
| [78_zamenhof-pri-homaro-i_d-ro-edmond-privat_gbia3015717a](https://archive.org/details/78_zamenhof-pri-homaro-i_d-ro-edmond-privat_gbia3015717a) | 131 | train |
| [78_zar-neznas-tango_dave-zupkovich-and-his-balkan-recording-artists-joe-matacic-anthon_gbia0447995a](https://archive.org/details/78_zar-neznas-tango_dave-zupkovich-and-his-balkan-recording-artists-joe-matacic-anthon_gbia0447995a) | 186 | train |
| [78_zauber-der-melodie_oskar-jerochnik-mit-seinen-rhythmikern-franz-marszalek_gbia7000531b](https://archive.org/details/78_zauber-der-melodie_oskar-jerochnik-mit-seinen-rhythmikern-franz-marszalek_gbia7000531b) | 1256 | train |
| [78_zebys-byla-moja-if-you-were-mine_frank-wojnarowski-i-jego-orkiestra_gbia0019137b](https://archive.org/details/78_zebys-byla-moja-if-you-were-mine_frank-wojnarowski-i-jego-orkiestra_gbia0019137b) | 49 | test |
| [78_zlote-slonce-golden-sun_ray-henry-ork.-r.--henry_gbia0002136b](https://archive.org/details/78_zlote-slonce-golden-sun_ray-henry-ork.-r.--henry_gbia0002136b) | 107 | test |
| [78_zote-rybki-polka-golden-fish-polka_john-nogaj-and-his-orchestra-john-nogaj-john-nog_gbia0529874a](https://archive.org/details/78_zote-rybki-polka-golden-fish-polka_john-nogaj-and-his-orchestra-john-nogaj-john-nog_gbia0529874a) | 18 | train |
| [95165-anday-befreit-strauss](https://archive.org/details/95165-anday-befreit-strauss) | 8 | train |
| [ACEckRobertsonSallieGoodenVictor18956](https://archive.org/details/ACEckRobertsonSallieGoodenVictor18956) | 562 | train |
| [BennoZieglerTraviata](https://archive.org/details/BennoZieglerTraviata) | 2 | train |
| [BernieCumminsOrchestraCollection1925-1935](https://archive.org/details/BernieCumminsOrchestraCollection1925-1935) | 1041 | train |
| [ErnaniPaseroB1305](https://archive.org/details/ErnaniPaseroB1305) | 70 | train |
| [Falling_312](https://archive.org/details/Falling_312) | 10 | test |
| [FaustRammentaILietiDio](https://archive.org/details/FaustRammentaILietiDio) | 32 | train |
| [Fertilizer](https://archive.org/details/Fertilizer) | 240 | train |
| [FinOlsen-ImHappyWhenImSinging-ErhardBauschkeTanzorchester](https://archive.org/details/FinOlsen-ImHappyWhenImSinging-ErhardBauschkeTanzorchester) | 1093 | train |
| [FleischerJanczak50288DieFristIstUm](https://archive.org/details/FleischerJanczak50288DieFristIstUm) | 1 | train |
| [FlowThouRegalPurpleStream](https://archive.org/details/FlowThouRegalPurpleStream) | 409 | train |
| [FranchiniAndDettbornPalakikoBluesRadiex4009](https://archive.org/details/FranchiniAndDettbornPalakikoBluesRadiex4009) | 366 | train |
| [FrankFererasHawaiiansSweetHawaiianMoonlightDomino0194](https://archive.org/details/FrankFererasHawaiiansSweetHawaiianMoonlightDomino0194) | 76 | train |
| [Gnadenarie](https://archive.org/details/Gnadenarie) | 151 | train |
| [HabaneraDeLIsleCarmen](https://archive.org/details/HabaneraDeLIsleCarmen) | 26 | train |
| [HarlanLeonardAndHisRocketsRockinWithTheRockets1940](https://archive.org/details/HarlanLeonardAndHisRocketsRockinWithTheRockets1940) | 164 | train |
| [HeiligtumDesHerzensO4818B](https://archive.org/details/HeiligtumDesHerzensO4818B) | 103 | train |
| [IgnacyPodgorskiIJegoNadzwyczajnaOrkiestraMalyMazLittleHusband1931](https://archive.org/details/IgnacyPodgorskiIJegoNadzwyczajnaOrkiestraMalyMazLittleHusband1931) | 76 | train |
| [IlFlautoMagicoGliAnguiDinferno](https://archive.org/details/IlFlautoMagicoGliAnguiDinferno) | 29 | test |
| [IllMakeDatBlackGirlMine](https://archive.org/details/IllMakeDatBlackGirlMine) | 8 | test |
| [ItsMineWhenYoureDoneWithIt](https://archive.org/details/ItsMineWhenYoureDoneWithIt) | 5 | train |
| [IveGotToGetMyselfSomebodyToLove](https://archive.org/details/IveGotToGetMyselfSomebodyToLove) | 20 | train |
| [JadlowkerHempelLuciaDuett](https://archive.org/details/JadlowkerHempelLuciaDuett) | 9 | train |
| [JimmieLuncefordOrchestra-FriscoFog](https://archive.org/details/JimmieLuncefordOrchestra-FriscoFog) | 21 | test |
| [JohnKAlmeidaAndHisHawaiiansMalihiniMele49thState69](https://archive.org/details/JohnKAlmeidaAndHisHawaiiansMalihiniMele49thState69) | 222 | test |
| [JosefGroenenFussreise62407](https://archive.org/details/JosefGroenenFussreise62407) | 77 | train |
| [KabaretowaOrkiestraRozmaitoscWalc1925](https://archive.org/details/KabaretowaOrkiestraRozmaitoscWalc1925) | 17 | train |
| [LetsStopTheClock-HoraceHeidtAndHisMusicalKnights-1939](https://archive.org/details/LetsStopTheClock-HoraceHeidtAndHisMusicalKnights-1939) | 1 | train |
| [LoveyCameBack](https://archive.org/details/LoveyCameBack) | 281 | train |
| [LuckyLindy](https://archive.org/details/LuckyLindy) | 40 | train |
| [MarshallPLufskyBirdiesFavoritePiccoloSoloOrchestraAccompanimentColumbiaA6313987May1909wav](https://archive.org/details/MarshallPLufskyBirdiesFavoritePiccoloSoloOrchestraAccompanimentColumbiaA6313987May1909wav) | 235 | train |
| [MaximMarsch](https://archive.org/details/MaximMarsch) | 70 | train |
| [MellowLittleDevil](https://archive.org/details/MellowLittleDevil) | 2000 | train |
| [Municipal_Band_Buenos_Aires-Auxilio-1911](https://archive.org/details/Municipal_Band_Buenos_Aires-Auxilio-1911) | 99 | train |
| [MysteriousEyes](https://archive.org/details/MysteriousEyes) | 139 | train |
| [OthelloSieSassMitLeideStckgold](https://archive.org/details/OthelloSieSassMitLeideStckgold) | 100 | train |
| [PaquitaZardo](https://archive.org/details/PaquitaZardo) | 9 | test |
| [a-45191-dalos-bela-morgenblatter](https://archive.org/details/a-45191-dalos-bela-morgenblatter) | 3 | train |
| [a-847-mardones-church-scene](https://archive.org/details/a-847-mardones-church-scene) | 3 | train |
| [c-2648-9-bartlett-robertson-bwv-1061](https://archive.org/details/c-2648-9-bartlett-robertson-bwv-1061) | 102 | train |
| [cajun-jitter-bug](https://archive.org/details/cajun-jitter-bug) | 15 | train |
| [christiansen-2](https://archive.org/details/christiansen-2) | 5 | train |
| [columbia-e-2002-38447](https://archive.org/details/columbia-e-2002-38447) | 508 | train |
| [crg-1007-8-emperors-new-clothes](https://archive.org/details/crg-1007-8-emperors-new-clothes) | 2000 | train |
| [cx-28-bizet-fair-maid-of-perth](https://archive.org/details/cx-28-bizet-fair-maid-of-perth) | 1092 | train |
| [da-1112-mc-cormack-to-the-children](https://archive.org/details/da-1112-mc-cormack-to-the-children) | 13 | train |
| [da-195-7-gould-deserted-ballroom](https://archive.org/details/da-195-7-gould-deserted-ballroom) | 92 | test |
| [da-8-walton-viola-concerto-iii](https://archive.org/details/da-8-walton-viola-concerto-iii) | 2000 | test |
| [daswarinheidelberg](https://archive.org/details/daswarinheidelberg) | 140 | train |
| [db-5623-herrmann-fliedermonolog](https://archive.org/details/db-5623-herrmann-fliedermonolog) | 27 | train |
| [db-6823-4-haydn-40-iii](https://archive.org/details/db-6823-4-haydn-40-iii) | 436 | train |
| [derliebeaugustin](https://archive.org/details/derliebeaugustin) | 613 | train |
| [dm-479-efco-mozart-sym-33-i](https://archive.org/details/dm-479-efco-mozart-sym-33-i) | 146 | train |
| [dobert-schlage-doch-gewuschte-stunde](https://archive.org/details/dobert-schlage-doch-gewuschte-stunde) | 18 | train |
| [dx-1137-8-cimarosa-benjamin-concerto](https://archive.org/details/dx-1137-8-cimarosa-benjamin-concerto) | 2000 | train |
| [edison-50043_01_3792](https://archive.org/details/edison-50043_01_3792) | 2000 | train |
| [edison-50051_01_3060](https://archive.org/details/edison-50051_01_3060) | 681 | train |
| [edison-50059_01_2877](https://archive.org/details/edison-50059_01_2877) | 2000 | train |
| [edison-50083_01_2362](https://archive.org/details/edison-50083_01_2362) | 2000 | test |
| [edison-50107_01_2335](https://archive.org/details/edison-50107_01_2335) | 1262 | train |
| [edison-50143_01_2539](https://archive.org/details/edison-50143_01_2539) | 2000 | train |
| [edison-50145_01_2593](https://archive.org/details/edison-50145_01_2593) | 910 | train |
| [edison-50146_01_2852](https://archive.org/details/edison-50146_01_2852) | 2000 | train |
| [edison-50186_01_3304](https://archive.org/details/edison-50186_01_3304) | 1540 | train |
| [edison-50191_01_3317](https://archive.org/details/edison-50191_01_3317) | 2000 | test |
| [edison-50239_01_3648](https://archive.org/details/edison-50239_01_3648) | 1210 | train |
| [edison-50255_01_3741](https://archive.org/details/edison-50255_01_3741) | 2000 | train |
| [edison-50270_01_3913](https://archive.org/details/edison-50270_01_3913) | 2000 | train |
| [edison-50319_01_4236](https://archive.org/details/edison-50319_01_4236) | 2000 | train |
| [edison-50395_01_5008](https://archive.org/details/edison-50395_01_5008) | 263 | train |
| [edison-50448_01_5727](https://archive.org/details/edison-50448_01_5727) | 583 | train |
| [edison-50458_01_5785](https://archive.org/details/edison-50458_01_5785) | 2000 | train |
| [edison-50479_01_6025](https://archive.org/details/edison-50479_01_6025) | 369 | train |
| [edison-50502_01_6474](https://archive.org/details/edison-50502_01_6474) | 2000 | train |
| [edison-50518_01_6591](https://archive.org/details/edison-50518_01_6591) | 2000 | train |
| [edison-50550_01_5699](https://archive.org/details/edison-50550_01_5699) | 1416 | test |
| [edison-50576_01_3415](https://archive.org/details/edison-50576_01_3415) | 2000 | train |
| [edison-50594_01_6877](https://archive.org/details/edison-50594_01_6877) | 2000 | train |
| [edison-50598_01_6422](https://archive.org/details/edison-50598_01_6422) | 2000 | train |
| [edison-50604_01_6043](https://archive.org/details/edison-50604_01_6043) | 1568 | train |
| [edison-50604_01_6044](https://archive.org/details/edison-50604_01_6044) | 2000 | train |
| [edison-50627_01_7002](https://archive.org/details/edison-50627_01_7002) | 1540 | train |
| [edison-50667_01_6994](https://archive.org/details/edison-50667_01_6994) | 2000 | test |
| [edison-50671_01_6114](https://archive.org/details/edison-50671_01_6114) | 1554 | train |
| [edison-50682_01_7123](https://archive.org/details/edison-50682_01_7123) | 2000 | train |
| [edison-50689_01_6920](https://archive.org/details/edison-50689_01_6920) | 1766 | train |
| [edison-50692_01_6045](https://archive.org/details/edison-50692_01_6045) | 1640 | train |
| [edison-50706_01_7424](https://archive.org/details/edison-50706_01_7424) | 942 | train |
| [edison-50710_01_7532](https://archive.org/details/edison-50710_01_7532) | 1365 | train |
| [edison-50724_01_7564](https://archive.org/details/edison-50724_01_7564) | 1047 | train |
| [edison-50825_01_8085](https://archive.org/details/edison-50825_01_8085) | 1084 | train |
| [edison-50833_01_8148](https://archive.org/details/edison-50833_01_8148) | 535 | train |
| [edison-50838_01_8132](https://archive.org/details/edison-50838_01_8132) | 1440 | train |
| [edison-50847_01_8158](https://archive.org/details/edison-50847_01_8158) | 2000 | train |
| [edison-50859_01_8074](https://archive.org/details/edison-50859_01_8074) | 2000 | train |
| [edison-50862_01_7161](https://archive.org/details/edison-50862_01_7161) | 2000 | test |
| [edison-50898_01_8226](https://archive.org/details/edison-50898_01_8226) | 2000 | train |
| [edison-50922_01_5996](https://archive.org/details/edison-50922_01_5996) | 2000 | train |
| [edison-51079_01_8639](https://archive.org/details/edison-51079_01_8639) | 2000 | train |
| [edison-51090_01_8657](https://archive.org/details/edison-51090_01_8657) | 2000 | train |
| [edison-51096_01_8613](https://archive.org/details/edison-51096_01_8613) | 2000 | train |
| [edison-51099_01_8671](https://archive.org/details/edison-51099_01_8671) | 1013 | train |
| [edison-51115_01_8689](https://archive.org/details/edison-51115_01_8689) | 2000 | train |
| [edison-51139_01_8881](https://archive.org/details/edison-51139_01_8881) | 1056 | train |
| [edison-51169_01_8532](https://archive.org/details/edison-51169_01_8532) | 2000 | train |
| [edison-51169_01_8585](https://archive.org/details/edison-51169_01_8585) | 2000 | train |
| [edison-51184_01_8997](https://archive.org/details/edison-51184_01_8997) | 1802 | train |
| [edison-51198_01_8741](https://archive.org/details/edison-51198_01_8741) | 2000 | train |
| [edison-51234_01_8754](https://archive.org/details/edison-51234_01_8754) | 2000 | test |
| [edison-51263_01_9214](https://archive.org/details/edison-51263_01_9214) | 2000 | train |
| [edison-51267_01_9193](https://archive.org/details/edison-51267_01_9193) | 1763 | train |
| [edison-51272_01_5406](https://archive.org/details/edison-51272_01_5406) | 2000 | train |
| [edison-51298_01_9341](https://archive.org/details/edison-51298_01_9341) | 2000 | train |
| [edison-51304_01_9377](https://archive.org/details/edison-51304_01_9377) | 2000 | train |
| [edison-51309_01_9319](https://archive.org/details/edison-51309_01_9319) | 2000 | train |
| [edison-51339_01_9456](https://archive.org/details/edison-51339_01_9456) | 1826 | test |
| [edison-51397_01_4997](https://archive.org/details/edison-51397_01_4997) | 2000 | train |
| [edison-51398_01_9686](https://archive.org/details/edison-51398_01_9686) | 2000 | train |
| [edison-51411_01_9724](https://archive.org/details/edison-51411_01_9724) | 841 | test |
| [edison-51415_01_9759](https://archive.org/details/edison-51415_01_9759) | 2000 | train |
| [edison-51445_01_9658](https://archive.org/details/edison-51445_01_9658) | 642 | train |
| [edison-51452_01_9878](https://archive.org/details/edison-51452_01_9878) | 2000 | train |
| [edison-51456_01_9887](https://archive.org/details/edison-51456_01_9887) | 2000 | train |
| [edison-51459_01_9790](https://archive.org/details/edison-51459_01_9790) | 1008 | train |
| [edison-51469_01_9895](https://archive.org/details/edison-51469_01_9895) | 462 | train |
| [edison-51574_01_10513](https://archive.org/details/edison-51574_01_10513) | 1502 | train |
| [edison-51585_01_10483](https://archive.org/details/edison-51585_01_10483) | 1329 | train |
| [edison-51644_01_10584](https://archive.org/details/edison-51644_01_10584) | 532 | test |
| [edison-51668_01_10669](https://archive.org/details/edison-51668_01_10669) | 2000 | train |
| [edison-51869_01_11056](https://archive.org/details/edison-51869_01_11056) | 1532 | test |
| [edison-51981_01_11578](https://archive.org/details/edison-51981_01_11578) | 2000 | train |
| [edison-52003_01_11657](https://archive.org/details/edison-52003_01_11657) | 2000 | train |
| [edison-52003_01_11658](https://archive.org/details/edison-52003_01_11658) | 2000 | train |
| [edison-52006_01_11655](https://archive.org/details/edison-52006_01_11655) | 1829 | train |
| [edison-52012_01_11668](https://archive.org/details/edison-52012_01_11668) | 494 | train |
| [edison-52048_01_11721](https://archive.org/details/edison-52048_01_11721) | 2000 | train |
| [edison-52145_01_18010](https://archive.org/details/edison-52145_01_18010) | 921 | train |
| [edison-52248_01_18245](https://archive.org/details/edison-52248_01_18245) | 652 | test |
| [edison-52315_01_18474](https://archive.org/details/edison-52315_01_18474) | 1456 | train |
| [edison-52345_01_18576](https://archive.org/details/edison-52345_01_18576) | 503 | train |
| [edison-52346_01_18592](https://archive.org/details/edison-52346_01_18592) | 946 | train |
| [edison-52362_01_18616](https://archive.org/details/edison-52362_01_18616) | 803 | train |
| [edison-52371_01_18637](https://archive.org/details/edison-52371_01_18637) | 379 | train |
| [edison-52418_01_18744](https://archive.org/details/edison-52418_01_18744) | 455 | train |
| [edison-52429_01_18780](https://archive.org/details/edison-52429_01_18780) | 2000 | train |
| [edison-52453_01_18890](https://archive.org/details/edison-52453_01_18890) | 642 | train |
| [edison-52461_01_18886](https://archive.org/details/edison-52461_01_18886) | 340 | train |
| [edison-52507_01_19011](https://archive.org/details/edison-52507_01_19011) | 264 | train |
| [edison-52514_01_19018](https://archive.org/details/edison-52514_01_19018) | 1057 | train |
| [edison-52527_01_19049](https://archive.org/details/edison-52527_01_19049) | 363 | train |
| [edison-52539_01_19083](https://archive.org/details/edison-52539_01_19083) | 981 | train |
| [edison-52570_01_19156](https://archive.org/details/edison-52570_01_19156) | 400 | train |
| [edison-52574_01_19163](https://archive.org/details/edison-52574_01_19163) | 458 | test |
| [edison-52595_01_19205](https://archive.org/details/edison-52595_01_19205) | 580 | train |
| [edison-52603_01_19229](https://archive.org/details/edison-52603_01_19229) | 1353 | train |
| [edison-52604_01_19219](https://archive.org/details/edison-52604_01_19219) | 295 | train |
| [edison-52617_01_19181](https://archive.org/details/edison-52617_01_19181) | 1471 | test |
| [edison-52645_01_19318](https://archive.org/details/edison-52645_01_19318) | 650 | train |
| [edison-58027_01_11556](https://archive.org/details/edison-58027_01_11556) | 2000 | train |
| [edison-60001_01_5408](https://archive.org/details/edison-60001_01_5408) | 2000 | train |
| [edison-60025_01_6396](https://archive.org/details/edison-60025_01_6396) | 2000 | train |
| [edison-60042_01_9802](https://archive.org/details/edison-60042_01_9802) | 2000 | train |
| [edison-65304_01_7936](https://archive.org/details/edison-65304_01_7936) | 2000 | train |
| [edison-65315_01_9432](https://archive.org/details/edison-65315_01_9432) | 1805 | train |
| [edison-76007_01_6547](https://archive.org/details/edison-76007_01_6547) | 2000 | train |
| [edison-76020_01_11006](https://archive.org/details/edison-76020_01_11006) | 2000 | train |
| [edison-78006_01_5042](https://archive.org/details/edison-78006_01_5042) | 2000 | train |
| [edison-80051_01_1264](https://archive.org/details/edison-80051_01_1264) | 1969 | train |
| [edison-80068_01_1322](https://archive.org/details/edison-80068_01_1322) | 2000 | train |
| [edison-80101_01_2296](https://archive.org/details/edison-80101_01_2296) | 1827 | train |
| [edison-80155_01_2792](https://archive.org/details/edison-80155_01_2792) | 2000 | train |
| [edison-80156_01_3674](https://archive.org/details/edison-80156_01_3674) | 1224 | train |
| [edison-80160_01_3117](https://archive.org/details/edison-80160_01_3117) | 2000 | train |
| [edison-80173_01_3015](https://archive.org/details/edison-80173_01_3015) | 2000 | train |
| [edison-80232_01_3459](https://archive.org/details/edison-80232_01_3459) | 2000 | train |
| [edison-80256_01_3972](https://archive.org/details/edison-80256_01_3972) | 2000 | train |
| [edison-80296_01_4275](https://archive.org/details/edison-80296_01_4275) | 1863 | train |
| [edison-80357_01_5613](https://archive.org/details/edison-80357_01_5613) | 1856 | train |
| [edison-80452_01_5285](https://archive.org/details/edison-80452_01_5285) | 1354 | train |
| [edison-80470_01_5334](https://archive.org/details/edison-80470_01_5334) | 2000 | train |
| [edison-80471_01_6684](https://archive.org/details/edison-80471_01_6684) | 2000 | train |
| [edison-80501_01_6927](https://archive.org/details/edison-80501_01_6927) | 932 | train |
| [edison-80535_01_7215](https://archive.org/details/edison-80535_01_7215) | 2000 | train |
| [edison-80539_01_7067](https://archive.org/details/edison-80539_01_7067) | 1055 | train |
| [edison-80561_01_7317](https://archive.org/details/edison-80561_01_7317) | 924 | train |
| [edison-80586_01_7036](https://archive.org/details/edison-80586_01_7036) | 2000 | train |
| [edison-80589_01_7392](https://archive.org/details/edison-80589_01_7392) | 1166 | train |
| [edison-80628_01_7672](https://archive.org/details/edison-80628_01_7672) | 1790 | train |
| [edison-80634_01_8153](https://archive.org/details/edison-80634_01_8153) | 1911 | train |
| [edison-80676_01_8177](https://archive.org/details/edison-80676_01_8177) | 1063 | train |
| [edison-80729_01_8209](https://archive.org/details/edison-80729_01_8209) | 2000 | train |
| [edison-80757_01_8480](https://archive.org/details/edison-80757_01_8480) | 2000 | train |
| [edison-80769_01_9216](https://archive.org/details/edison-80769_01_9216) | 2000 | train |
| [edison-80769_01_9217](https://archive.org/details/edison-80769_01_9217) | 2000 | train |
| [edison-80771_01_5979](https://archive.org/details/edison-80771_01_5979) | 2000 | test |
| [edison-80774_01_9285](https://archive.org/details/edison-80774_01_9285) | 726 | train |
| [edison-80806_01_10042](https://archive.org/details/edison-80806_01_10042) | 2000 | train |
| [edison-80823_01_9911](https://archive.org/details/edison-80823_01_9911) | 2000 | train |
| [edison-80846_01_10279](https://archive.org/details/edison-80846_01_10279) | 2000 | train |
| [edison-80848_01_10544](https://archive.org/details/edison-80848_01_10544) | 433 | test |
| [edison-80897_01_18331](https://archive.org/details/edison-80897_01_18331) | 2000 | train |
| [edison-82043_01_2394](https://archive.org/details/edison-82043_01_2394) | 2000 | train |
| [edison-82203_01_7268](https://archive.org/details/edison-82203_01_7268) | 1959 | train |
| [edison-82211_01_5961](https://archive.org/details/edison-82211_01_5961) | 2000 | train |
| [edison-82214_01_4947](https://archive.org/details/edison-82214_01_4947) | 2000 | train |
| [edison-82226_01_7525](https://archive.org/details/edison-82226_01_7525) | 2000 | train |
| [edison-82231_01_7748](https://archive.org/details/edison-82231_01_7748) | 2000 | train |
| [edison-82257_01_6840](https://archive.org/details/edison-82257_01_6840) | 2000 | train |
| [edison-82263_01_2407](https://archive.org/details/edison-82263_01_2407) | 2000 | train |
| [edison-82270_01_2010](https://archive.org/details/edison-82270_01_2010) | 1449 | train |
| [edison-82271_01_8457](https://archive.org/details/edison-82271_01_8457) | 2000 | train |
| [edison-82272_01_6586](https://archive.org/details/edison-82272_01_6586) | 2000 | train |
| [edison-82346_01_10843](https://archive.org/details/edison-82346_01_10843) | 462 | train |
| [edison-82351_01_19050](https://archive.org/details/edison-82351_01_19050) | 660 | train |
| [edison-83066_01_5288](https://archive.org/details/edison-83066_01_5288) | 2000 | train |
| [eg-3810-dorsch-einen-sommer-lang](https://archive.org/details/eg-3810-dorsch-einen-sommer-lang) | 56 | train |
| [emil-severin-ein-volk-von-brudern-wolln-wir-sein-leid-homokord-15864-a-171019](https://archive.org/details/emil-severin-ein-volk-von-brudern-wolln-wir-sein-leid-homokord-15864-a-171019) | 1070 | train |
| [emma-eames-who-is-sylvia-victrola-88013-1905](https://archive.org/details/emma-eames-who-is-sylvia-victrola-88013-1905) | 464 | train |
| [enric-madriguera-and-his-orchestra-danza-lucumi-rca-victor-27487-b](https://archive.org/details/enric-madriguera-and-his-orchestra-danza-lucumi-rca-victor-27487-b) | 129 | test |
| [enric-madriguera-and-his-orchestra-no-no-no-rca-victor-27702-a](https://archive.org/details/enric-madriguera-and-his-orchestra-no-no-no-rca-victor-27702-a) | 1366 | train |
| [enric-madriguera-and-his-orchestra-someday-ill-meet-you-again-hit-7077-cr-357](https://archive.org/details/enric-madriguera-and-his-orchestra-someday-ill-meet-you-again-hit-7077-cr-357) | 218 | train |
| [f.-4074-a-charlie-kunz-piano-medley-no.-d.-110-pt.-1-r-15187685](https://archive.org/details/f.-4074-a-charlie-kunz-piano-medley-no.-d.-110-pt.-1-r-15187685) | 2000 | train |
| [fado-de-santa-cruz-bettencourt](https://archive.org/details/fado-de-santa-cruz-bettencourt) | 8 | train |
| [famous-3127-b-swanee-river-moon](https://archive.org/details/famous-3127-b-swanee-river-moon) | 356 | train |
| [feldpostfurannchen](https://archive.org/details/feldpostfurannchen) | 263 | train |
| [filmzauber-kennengelernt](https://archive.org/details/filmzauber-kennengelernt) | 26 | train |
| [fonodan-vme-1501-bach-preludes-fugues-bwv-555-558-videroe](https://archive.org/details/fonodan-vme-1501-bach-preludes-fugues-bwv-555-558-videroe) | 2 | test |
| [francis-koene-col-d-17187-beethoven](https://archive.org/details/francis-koene-col-d-17187-beethoven) | 1 | train |
| [frank-luther-trio-crime-does-not-pay-oriole-15457-1-8364-b](https://archive.org/details/frank-luther-trio-crime-does-not-pay-oriole-15457-1-8364-b) | 69 | train |
| [fruhlingsrausch](https://archive.org/details/fruhlingsrausch) | 1 | train |
| [ind-1062](https://archive.org/details/ind-1062) | 6 | train |
| [inderpfalz](https://archive.org/details/inderpfalz) | 211 | train |
| [irvinggilmore07](https://archive.org/details/irvinggilmore07) | 1 | test |

## Clean music: 397 netlabels releases

| Item | Licence | Split |
| --- | --- | --- |
| [AUDIOPESTE. GARATGE 23.IV.1994 - AUDIOPESTE](https://archive.org/details/16rpm_adp_gar) | http://creativecommons.org/licenses/publicdomain/ | train |
| [28 Sept. 2016, driveway at night - 'man met baard'](https://archive.org/details/20160928DrivewayAtNight) | http://creativecommons.org/licenses/by/3.0/ | train |
| [629 Piers - Yukiga Futte Uresii](https://archive.org/details/629Piers) | http://creativecommons.org/licenses/by/4.0/ | train |
| [ONE BBSCON 1993: History and Lore of the BBS - Ward Christensen, Nick Anis, Chuck Forsberg](https://archive.org/details/93bbscon-bbshistory) | None | train |
| [AA083](https://archive.org/details/AA083_20140226) | None | train |
| [A Darker Shade Of Tao - The Peach Tree](https://archive.org/details/ADarkerShadeOfTao) | http://creativecommons.org/licenses/by-nc-sa/2.5/au/ | train |
| [Songs For Little Night Explorers - The Dandelion Council](https://archive.org/details/AH028_The_Dandelion_Council_-_Songs_For_Little_Night_Explorers) | None | train |
| [AKA/etc. - Sara Ayers](https://archive.org/details/AKAetc) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | test |
| [Lithium Toolbox Volume II (ARGREC18) - John Lithium](https://archive.org/details/ARGREC18) | http://creativecommons.org/licenses/by/4.0/ | test |
| [ARTEFACTO-ARTEFACTO - ARTEFACTO](https://archive.org/details/ARTEFACTO-ARTEFACTO) | http://creativecommons.org/licenses/by-nc/3.0/ | train |
| [Abanico](https://archive.org/details/Abanico) | None | train |
| [DJ_Iterate - All Soul Letter [752] - Thomas Park](https://archive.org/details/All_Soul_Letter) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [05_mobdividual_Alvar_Aalto - Brian Elyo mobdividual](https://archive.org/details/Alvar_Aalto) | None | train |
| [Ann Or Lunda- Ann Or Lunda [treetrunk 603] - Ann Or Lunda](https://archive.org/details/Ann_Or_Lunda) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Mystified- Cereal For Dinner [Archival Selections 004] - Thomas Park](https://archive.org/details/ArchivalSelections004) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Mystified- Eldritch Steps [Archival Selections 007] - Thomas Park](https://archive.org/details/ArchivalSelections007) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Mystified- Fragment, Compress [Archival Selections 009] - Thomas Park](https://archive.org/details/ArchivalSelections009) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Mystified- Tropical Depression [Archival Selections 018] - Thomas Park](https://archive.org/details/ArchivalSelections018) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Mystified- Moonshine [Archival Selections 023] - Thomas Park](https://archive.org/details/ArchivalSelections023) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Digital Mass- The Murk [Archival Selections 026] - Thomas Park](https://archive.org/details/ArchivalSelections026) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Meho - Are We Alone : [cz016] - Meho](https://archive.org/details/AreWeAlone) | http://creativecommons.org/licenses/by/3.0/ | test |
| [ARRACH@Bikini 01/04/2009 - Arrach](https://archive.org/details/ArrachBikiniAvril2009) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Ayankoko- Audio Transmission Smells (2009) - Ayankoko](https://archive.org/details/Ayankoko-AudioTransmissionSmells2009) | http://creativecommons.org/licenses/by/2.0/fr/ | train |
| [AZUCENA 300 VECES - AZUCENA 300 VECES - AZUCENA 300 VECES](https://archive.org/details/Azucena300Veces-Azucena300Veces) | http://creativecommons.org/licenses/by-nc/3.0/ | train |
| [A Brief Soundscape of Humanity - Cheap Polaroid](https://archive.org/details/BFTG_124) | https://creativecommons.org/licenses/by-sa/4.0/ | train |
| [2003 Toyota Corolla (Remixes) - 2003 Toyota Corolla](https://archive.org/details/BFTG_197) | https://creativecommons.org/licenses/by-sa/4.0/ | train |
| [2003 Toyota Corolla (Terexxa Remix) - 2003 Toyota Corolla](https://archive.org/details/BFTG_200) | https://creativecommons.org/licenses/by-sa/4.0/ | train |
| [Internet Culture - Cadaver](https://archive.org/details/BFTG_232) | https://creativecommons.org/licenses/by-sa/4.0/ | train |
| [PZA: THE NEXT SLICE - PZA](https://archive.org/details/BFTG_72) | None | train |
| [Bandit the Panther - 1-Up The Punks - Bandit the Panther](https://archive.org/details/BanditThePanther-1UpThePunks) | None | train |
| [Thomas Park- Bermuda 11292019 [treetrunk 475] - Thomas Park](https://archive.org/details/Bermuda11292019) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Bill A & 24​/​7 - Fellirium](https://archive.org/details/Bill_A_24_7) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Boarstusk - Boarstusk / Hologram Reality - Boarstusk](https://archive.org/details/BoarstuskHologramReality) | None | test |
| [INVERSION DE PHASE STARRING Jack Dentic QDB 03.2016 Live Bootleg - BBS](https://archive.org/details/Bootleg_20160317) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [CDGelements038 - Lucas Darklord](https://archive.org/details/CDGelements038) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [Burning Rome - Surface pt1 - Burning Rome](https://archive.org/details/COTN001) | http://creativecommons.org/licenses/by-nc-nd/3.0/us/ | train |
| [Cambodian Vein Ritual - Yukiga Futte Uresii](https://archive.org/details/CambodianVeinRitual) | http://creativecommons.org/licenses/by/3.0/ | train |
| [CATASTROFE CLUB - GALLETAS - CATASTROFE CLUB](https://archive.org/details/CatastrofeClubGalletas) | http://creativecommons.org/licenses/by-nc/3.0/ | train |
| [Cinturon Negro Cold People (mixtape)](https://archive.org/details/CinturonNegroColdPeople) | None | train |
| [CittaDelFututro by M. Croce (oz012) 2008 - Massimo Croce](https://archive.org/details/CittadelfututroByM.Croceoz0132008) | http://creativecommons.org/licenses/publicdomain/ | train |
| [Scott Lawlor- Complex Silence 36 [treetrunk 272] - Scott Lawlor](https://archive.org/details/Complex_Silence_36) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | test |
| [Grove Of Whispers- Complex Silence 39 [treetrunk 284] - Grove Of Whispers](https://archive.org/details/Complex_Silence_39) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Controlled Blue Lava - Yukiga Futte Uresii](https://archive.org/details/ControlledBlueLava) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Cosmetics For Nullifidian - Yukiga Futte Uresii](https://archive.org/details/CosmeticsforNullifidian) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Live à la Ferme Electrique 07/07/2017 - Stratocastors](https://archive.org/details/DEGl024) | None | train |
| [DJ_Iterate- Wormsign [treetrunk 542] - Thomas Park](https://archive.org/details/DJIterateWormsign) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Dan Miñoza - Tulpa - Dan Miñoza](https://archive.org/details/Dan_Minoza_Tulpa) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [DECURS - SATANA - DECURS](https://archive.org/details/DecursSatana) | http://creativecommons.org/licenses/by-nc/3.0/ | train |
| [Der Spaziergang 4 - malaventura](https://archive.org/details/Derspaziergang4) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [泥にも縋る - Yukiga Futte Uresii](https://archive.org/details/DoroNimoSugaru) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Dust. Time.. Gravity - The Ghost of an Alien](https://archive.org/details/Dust-Time-Gravity) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Eyewitnesses Became an Ice Pillar after Crawl Out from the Pothole - Yukiga Futte Uresii](https://archive.org/details/EBaIPaCOftP) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Thomas Park- EDG2242022 [treetrunk 735] - Thomas Park](https://archive.org/details/EDG2242022) | http://creativecommons.org/publicdomain/mark/1.0/ | test |
| [Eienni Uruou - Yukiga Futte Uresii](https://archive.org/details/EienniUruou) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Thomas Park- Emerging From The Landscape [treetrunk 810] - Thomas Park](https://archive.org/details/EmergingFromTheLandscape) | https://creativecommons.org/publicdomain/mark/1.0/ | train |
| [DJ Frankenstone- Encrypted Transmission [treetrunk 748] - Thomas Park](https://archive.org/details/Encrypted_Transmission) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Thomas Park- Endless Dub Generation 5.30.2021 [treetrunk 671] - Thomas Park](https://archive.org/details/EndlessDubGeneration5302021) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [EugeneKha - Sevastopol Sunrise (Live 2017) - EugeneKha](https://archive.org/details/Eugenekha-SevastopolSunriselive2017) | http://creativecommons.org/licenses/by-nc-sa/4.0/ | train |
| [FASHION_KORPS-DEMONISTS - FASHION_KORPS](https://archive.org/details/FASHION_KORPS-DEMONISTS) | http://creativecommons.org/licenses/by-nc/3.0/ | test |
| [VA - powered UP!! - 2012](https://archive.org/details/FBA_VA01) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Astrobastards & Assholes - Stratosonics](https://archive.org/details/FW100-4_Stratosonics) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [Spazieren im Filterwunderland - Kopfklang](https://archive.org/details/FW101_Kopfklang) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [Facalongen - Yukiga Futte Uresii](https://archive.org/details/Facalongen) | http://creativecommons.org/licenses/by/2.1/jp/ | train |
| [Catriel Nievas peformed by Nacho Castillo - Favourite Guitar - Catriel Nievas](https://archive.org/details/FavouriteGuitar-catrielnievas) | None | train |
| [Mystified- Fractal Techno [treetrunk 277] - Mystified](https://archive.org/details/Fractal_Techno) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [frei²: The Return Of Electro - DJ Robb](https://archive.org/details/Freihoch2-TheReturnOfElectro) | http://creativecommons.org/licenses/by-nc-sa/3.0/de/ | train |
| [DJ_Iterate- Funk and Bass [treetrunk 596] - Thomas Park](https://archive.org/details/FunkAndBass) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Adam Weishaupt's Psychedelic Supper GHGR 017916 - Hopalong Horus Heisenberg](https://archive.org/details/GHGR017916) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [GIR030MollyRingwormViolencePovertyBoogie - Molly Ringworm](https://archive.org/details/GIR030MollyRingwormViolencePovertyBoogie) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [[GT1269] Vziel Projet — Пространство](https://archive.org/details/GT1269) | None | test |
| [SH010 - Gerardo Figueroa plays Farabeuf](https://archive.org/details/GerardoFigueroaPlaysFarabeuf_284) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [Glitterbug - The Moon Studios Sessions - Glitterbug](https://archive.org/details/Glitterbug-TheMoonStudiosSessions) | None | test |
| [Grid Resistor- Phi [treetrunk 377] - Grid Resistor](https://archive.org/details/GridResistorPhi) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [wenteltrap - nonkel waldek](https://archive.org/details/HILIV007) | https://creativecommons.org/licenses/by-nc-sa/4.0/ | train |
| [Thomas Park With Harry Partch- Harry Partch Iterations [treetrunk 504] - Thomas Park](https://archive.org/details/HarryPartchIterations) | https://creativecommons.org/licenses/by/4.0/ | train |
| [Thomas Park- Haunted Heights [treetrunk 459] - Thomas Park](https://archive.org/details/Haunted_Heights) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Here I go - half past sun](https://archive.org/details/HereIGo) | http://creativecommons.org/licenses/by-nc/3.0/ | train |
| [ヘルゲート - Yukiga Futte Uresii](https://archive.org/details/Heruge_to) | https://creativecommons.org/licenses/by/4.0/ | train |
| [hkair - ep2 - hkair](https://archive.org/details/Hkair-Ep2) | http://creativecommons.org/licenses/by-nc-nd/3.0/de/ | train |
| [Hunting the hare - Traditional english](https://archive.org/details/Hunting_the_hare) | None | train |
| [Hypothesis Ash Spot - Charles Rice Goff III](https://archive.org/details/HypothesisAshSpot) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [I Don't Know What To Do YES YES YES!! - Yukiga Futte Uresii](https://archive.org/details/IDKWTDYYY) | https://creativecommons.org/licenses/by/4.0/ | train |
| [Music for Impossible Orchestra - Impossible Orchestra](https://archive.org/details/ImpossibleOrchestraMusicforImpossibleOrchestra) | http://creativecommons.org/licenses/by-nc/2.5/ | train |
| [Thomas Park- In Pursuit Of Desert Demons [treetrunk 821] - Thomas Park](https://archive.org/details/In_Pusuit_Of_Desert_Demons) | https://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Indecision - Frequency Cheque - Indecision](https://archive.org/details/Indecision-FrequencyCheque) | None | train |
| [Intravene - Spilling From A Shattered Sky - Intravene](https://archive.org/details/Intravene-SpillingFromAShatteredSky) | https://creativecommons.org/licenses/by-nd/4.0/ | train |
| [シーサイドマジック - 絡み合った運命 & 花畑](https://archive.org/details/KaramiattaUnmei-Hanahata-Shiisaidomajikku) | None | train |
| [KIBO - Knowledge In Bullshit Out - KIBO](https://archive.org/details/KnowledgeInBullshitOut) | http://creativecommons.org/licenses/by/2.5/ | train |
| [Kohoxo - Yukiga Futte Uresii](https://archive.org/details/Kohoxo) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Kou Iu Notte - Yukiga Futte Uresii](https://archive.org/details/KouIuNotte) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Benjamin Ramadani live at Brand [LH004] - Benjamin Ramadani](https://archive.org/details/LH004) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [eila rmx](https://archive.org/details/LSD002) | None | train |
| [Le Strida Live Cairo 09_oz020 - Le Strida](https://archive.org/details/LeStridaLiveCairo09_oz020) | http://creativecommons.org/licenses/publicdomain/ | train |
| [Lost and Salvaged #01 - An Indonesian Song - Yukiga Futte Uresii](https://archive.org/details/LoanSa01) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Lost and Salvaged #02 - Glass Bear - Yukiga Futte Uresii](https://archive.org/details/LoanSa02) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Lost and Salvaged #05 - Tiny Pill-Sized Plasma Bulb - Yukiga Futte Uresii](https://archive.org/details/LoanSa05) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Lost and Salvaged #09 - Return When Tablets are - Yukiga Futte Uresii](https://archive.org/details/LoanSa09) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Lost and Salvaged #12 - Wave Output - Yukiga Futte Uresii](https://archive.org/details/LoanSa12) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Lost and Salvaged #13 - Zero Zero - Yukiga Futte Uresii](https://archive.org/details/LoanSa13) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Thomas Park- Loopworks 2 [treetrunk 404] - Thomas Park](https://archive.org/details/Loopworks02) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [A Song For Our Hopeless Desperation - Lost Trail](https://archive.org/details/LostTrailLamentationsPart2) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Pearl - the Maravines, Worm's Eye View](https://archive.org/details/MARAV001A) | http://creativecommons.org/publicdomain/mark/1.0/ | test |
| [Who's Listening Now? - the Maravines](https://archive.org/details/MARAV002S) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Bruce - the Maravines](https://archive.org/details/MARAV012A) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [BlowUpRadio Live Set - the Maravines, Fairmont](https://archive.org/details/MARAV024L) | https://creativecommons.org/licenses/by/4.0/ | train |
| [Live at the Court Tavern - the Maravines](https://archive.org/details/MARAV025L) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Sweaters & Sweets Coffeehouse Show - the Maravines](https://archive.org/details/MARAV026L) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Attic Session - the Maravines](https://archive.org/details/MARAV046R) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Chernobyl - the Red Light](https://archive.org/details/MARAV994D) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [The Pressure Machine - the Pressure Machine](https://archive.org/details/MARAV999D) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [капитан Trip - Erotica (2014) [MNMN295] - капитан Trip](https://archive.org/details/MNMN295) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Mechanical Animals feat. Михаил Цы - Противоядие (2014) [MNMN296] - Mechanical Animals feat. Михаил Цы](https://archive.org/details/MNMN296) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | test |
| [aspiration beat - KAMIKAZE (2015) [MNMN315] - aspiration beat](https://archive.org/details/MNMN315) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [MNMN RECORDS NETLABEL - HAPPY BIRTHDAY COMPILATION (2015) [MNMN347] - Various Artists](https://archive.org/details/MNMN347) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Nordgroove - Kepper of the Samples (2016) [MNMN376] - Nordgroove](https://archive.org/details/MNMN376) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Ilya Id - Cronenbergus (2016) [MNMN394] - Ilya Id](https://archive.org/details/MNMN394) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [MNMN RECORDS NETLABEL - л е т о / e n d (2016) [MNMN397] - Various Artists](https://archive.org/details/MNMN397) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [РВЁМ ТАНЦПОЛ - I Dont Give a Fuck (2017) [MNMN431] - РВЁМ ТАНЦПОЛ](https://archive.org/details/MNMN431) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Risssing - Music for MNMN (2018) [MNMN505] - Risssing](https://archive.org/details/MNMN505) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | test |
| [a.eer - foreigner (2017) [MNMN444] - a.eer](https://archive.org/details/MNMN_444) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Dreamfish - Atom Sphere {MOD#22} - Dreamfish](https://archive.org/details/MOD22) | None | train |
| [Mortimer Twang - Theme {MOD#41} - Mortimer Twang](https://archive.org/details/MOD41) | None | train |
| [MRDN003 / North Pole Weather Forecast The Ice Trilogy Part Two Isolation](https://archive.org/details/MRDN003NorthPoleWeatherForecastTheIceTrilogyPartTwoIsolation) | http://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Keith303 - Anxiety Express {MUL#05} - Keith303](https://archive.org/details/MUL05) | None | train |
| [Ramone - Crazy Juice {MUL#09} - Ramone](https://archive.org/details/MUL09) | None | train |
| [Salaam Shalom - malaventura](https://archive.org/details/MalaventuraSalaamShalom) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [mam184 - John Praw - Fireworks (2011) - John Praw](https://archive.org/details/Mam184-JohnPraw-Fireworks2011) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | test |
| [mam192 - bell monks - 08/11 august (2011) - bell monks](https://archive.org/details/Mam192-BellMonks-0811August2011) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Mantra Ray - Mantra - TAS#0002 - Mantra Ray and TheAcridSound](https://archive.org/details/MantraRay-Mantra-Tas0002) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Markus Schwill Live @ Eisenbahner 19951224](https://archive.org/details/Markus_Schwill_Live_Eisenbahner_19951224) | None | train |
| [Mash Gordon - Actionbratwurstkids - tipsypoodl](https://archive.org/details/MashgordonActionbratwurstkids) | http://creativecommons.org/licenses/by-nc-sa/4.0/ | train |
| [DJ_Iterate- Mass Modern World [treetrunk 691] - Thomas Park](https://archive.org/details/Mass_Modern_World) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Meho - Hibernation : [cz017] - Meho](https://archive.org/details/Meho-Hibernationcz017) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Meho - MKUltra [cz015] - Meho](https://archive.org/details/Meho-Mkultracz015) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Meho - Terra Nullius : [cz20] - Meho](https://archive.org/details/Meho-TerraNulliuscz20) | http://creativecommons.org/licenses/by/4.0/ | test |
| [Thomas Park- Memories In Blue And Green [treetrunk 636] - Thomas Park](https://archive.org/details/MemoriesInBlueAndGreen) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Mescaline Sessions - Decaying Culture [cz001] - Mescaline Sessions](https://archive.org/details/MescalineSessions-DecayingCulturecz001) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Mescaline Sessions - Session 12 -16 (Banja Luka Sessions) : [cz018] - Mescaline Sessions](https://archive.org/details/MescalineSessions-Session12-16banjaLukaSessionscz018) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Thomas Park- Moody Recursion Associated Material [treetrunk 736] - Thomas Park](https://archive.org/details/MoodyRecursionAssociatedMaterial) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Music For Headphones Volume One [TWX017] - FULCRUM](https://archive.org/details/MusicForHeadphonesVolumeOne) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Mystified with Christopher Alvarado- The Mystical Recursion Remixes [treetrunk 340] - Mystified with Christoph](https://archive.org/details/MysticalRecursionRemixes) | http://creativecommons.org/licenses/by/3.0/ | test |
| [Mystified- Bones [treetrunk 518] - Thomas Park](https://archive.org/details/MystifiedBones) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Mystified- Sovereign [treetrunk 336] - mystified](https://archive.org/details/MystifiedSovereign) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [NoiShanghai X 08-05-2006 - bivouacmusic](https://archive.org/details/NOIShanghai_X) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [Nebula Of Irrationality Seems Eternal - The Goff Mix - Total E.T.](https://archive.org/details/NebulaOfIrrationalitySeemsEternal-TheGoffMix) | http://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [No Damage Clear - Yukiga Futte Uresii](https://archive.org/details/NoDamageClear) | http://creativecommons.org/licenses/by/4.0/ | train |
| [DJ_Iterate- Noble Enforcement Painted Energy [treetrunk 707] - DJ_Iterate](https://archive.org/details/Noble_Enforcement_Painted_Energy) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Thomas Park- Normal People [treetrunk 405] - Thomas Park](https://archive.org/details/NormalPeople) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [OUR LADY OF DEATH - AAVV](https://archive.org/details/OURLADYOFDEATH) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Oisii Kemuri - Yukiga Futte Uresii](https://archive.org/details/OisiiKemuri) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Thomas Park- On Cold Baltic Seas [treetrunk 797] - Thomas Park](https://archive.org/details/OnColdBalticSeas) | https://creativecommons.org/publicdomain/mark/1.0/ | train |
| [女の肉から搾った膏 - Yukiga Futte Uresii](https://archive.org/details/OnnanoNikukaraSibottaAbura) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Thomas Park- Opium, Hash And Imminent Peril [treetrunk 788] - Thomas Park](https://archive.org/details/OpiumHashAndImminentPeril) | https://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Thomas Park- Organic Dissonance [treetrunk 441] - Thomas Park](https://archive.org/details/Organic_Dissonance) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Orquesta de Perros - Roles y Oficios - Lautaro Barcelo, Pablo Mati­as Vidal, Pablo La Ferrara, German Pasalagu](https://archive.org/details/OrquestaDePerros-RolesYOficios) | http://creativecommons.org/licenses/by/3.0/ | train |
| [DJ_Iterate- Over Easy [treetrunk 604] - Thomas Park](https://archive.org/details/OverEasy) | http://creativecommons.org/publicdomain/mark/1.0/ | test |
| [Rotten From Within - Crimson Stain](https://archive.org/details/PHAQEP13) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [Rust and Ore - Dispersal - Rust and Ore](https://archive.org/details/PILOTELEVEN_011) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Peo Voz](https://archive.org/details/PeoVoz_201802) | None | test |
| [Prairie - Vimana Aircraft](https://archive.org/details/Prairie-VimanaAircraft) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Remisturas - Quarto Nove Ilda.](https://archive.org/details/Quarto_Nove_Ilda._-_Remisturas) | http://creativecommons.org/licenses/by-nd/4.0/ | train |
| [Various Artists - Mortimeremixed EP Vol.2 {REL#129} - Various Artists](https://archive.org/details/REL129) | None | train |
| [ST17 My Darling / My Divine by Radere - Radere](https://archive.org/details/RadereMyDarlingMyDivine) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Such a Parcel of Rogues in a Nation - Stuart Eydmann](https://archive.org/details/RaretunesEydmannSuchaparcel) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [DJ Frankenstone- Recent Identical Visual [treetrunk 711] - Thomas Park](https://archive.org/details/Recent_Identical_Visual) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Thomas Park- Recursive Drones [treetrunk 422] - Thomas Park](https://archive.org/details/RecursiveDrones) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [DJ_Iterate- RetroFract [treetrunk 544] - Thomas Park](https://archive.org/details/RetroFract) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Right Turn Clyde - 3 EP - Right Turn Clyde](https://archive.org/details/RightTurnClyde-3EP) | None | train |
| [Rizoma - Miguel Isaza](https://archive.org/details/Rizoma_201905) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Adrian Chevalier & Evgenia Pavlova - La Rose Noire (Single, 2013) [SCL104] - Adrian Chevalier](https://archive.org/details/SCL104) | http://creativecommons.org/licenses/by-nc-sa/4.0/ | train |
| [Psi Side - Sound Pressure Level](https://archive.org/details/SDR003) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | test |
| [SICMON008](https://archive.org/details/SICMON008) | http://creativecommons.org/publicdomain/zero/1.0/ | train |
| [[SR040] Chainsaw Penetration - Anthropocene (2018) - Chainsaw Penetration](https://archive.org/details/SPUTNIKRECORDS040) | http://creativecommons.org/publicdomain/zero/1.0/ | train |
| [SR21 - SLP - Deliverance of the Self - SLP](https://archive.org/details/SR22-SLP-Deliverance) | http://creativecommons.org/licenses/by-nd/3.0/ | train |
| [Artificial.Music - Curtains - Artificial.Music](https://archive.org/details/SRS07907) | https://creativecommons.org/licenses/by/4.0/ | train |
| [Babasmas & Caturday - A Turtle's Adventures - Babasmas & Caturday](https://archive.org/details/SRS09502) | https://creativecommons.org/licenses/by-sa/4.0/ | train |
| [Ashiera - Route 205 - Ashiera](https://archive.org/details/SRS09713) | https://creativecommons.org/licenses/by/4.0/ | train |
| [Artificial.Music - Faithful Mission - Artificial.Music](https://archive.org/details/SRS12707) | https://creativecommons.org/licenses/by/4.0/ | train |
| [Artificial.Music & lo'fi boy - Compromise - Artificial.Music & lo'fi boy](https://archive.org/details/SRS16807) | https://creativecommons.org/licenses/by/4.0/ | train |
| [Ash Electric - This Is Retro Electro Vol. 1 - Ash Electric](https://archive.org/details/SRS20313) | None | train |
| [The Three Virtues of Incompetence - rr.gross](https://archive.org/details/SSSDlp11_-_VoI) | http://creativecommons.org/licenses/by-nc-sa/4.0/ | train |
| [Thomas Park- San Francisco Skyline [treetrunk 612] - Thomas Park](https://archive.org/details/SanFranciscoSkyline) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Saturation Saturday - Various Artists](https://archive.org/details/SaturationSaturday) | http://creativecommons.org/publicdomain/zero/1.0/ | train |
| [スキャニン・ダズリン - Yukiga Futte Uresii](https://archive.org/details/ScaninDuzzlin) | http://creativecommons.org/licenses/by/4.0/ | test |
| [Thomas Park- Shadows In The Lounge [treetrunk 782] - Thomas Park](https://archive.org/details/Shadows_In_The_Lounge) | https://creativecommons.org/publicdomain/mark/1.0/ | train |
| [SH024 - Sheep :: Netlabel - Compilado para el 7° Aniversario - Varios Artistas](https://archive.org/details/SheepNetlabel-CompiladoParaEl7Aniversario) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [ｒｅｐｅｎｔａｎｃｅ - 死 C O M P U T E R 死](https://archive.org/details/ShiCOMPUTERShi-repentance) | None | train |
| [DJ_Iterate- SleepNet [treetrunk 626] - Thomas Park](https://archive.org/details/SleepNet) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Thomas Park- Sound Collage Science [treetrunk 444] - Thomas Park](https://archive.org/details/SoundCollageScience) | http://creativecommons.org/publicdomain/mark/1.0/ | test |
| [SuqElGomabyM.Croce(oz017)2009 - Massimo Croce](https://archive.org/details/SuqElGomabyM.Croceoz0172009) | http://creativecommons.org/licenses/publicdomain/ | train |
| [Sweet for the wild - Another Record](https://archive.org/details/Sweets_for_the_wild) | None | train |
| [書架のディテール (Syoka no Detail) - Yukiga Futte Uresii](https://archive.org/details/SyokanoDetail) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Traditional Gaida Breathing, Pt. 3: Admande Gustau - Yukiga Futte Uresii](https://archive.org/details/TGBpt3) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Tedious Turbulence - Charles Rice Goff III](https://archive.org/details/TediousTurbulence) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Thomas Park- The Adventures Of Fatty And Bronstein [treetrunk 442] - Thomas Park](https://archive.org/details/TheAdventuresOfFattyAndBronstein) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Erik Satie With Thomas Park- The Gymnopedies Iterations [treetrunk 418] - Thomas Park](https://archive.org/details/TheGymnopediesIterations) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [ジ・アザー・サイド・オブ・太陽と処罰感情 - Yukiga Futte Uresii](https://archive.org/details/TheOtherSideofTS) | http://creativecommons.org/licenses/by/4.0/ | train |
| [The Space-Erly Brothers - Charles Rice Goff III & Lord Litter](https://archive.org/details/TheSpace-erlyBrothers) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Thomas Park- The Spin Tribe [treetrunk 455] - Thomas Park](https://archive.org/details/TheSpinTribe) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Grove Of Whispers- The Radiant [treetrunk 254] - Grove Of Whispers](https://archive.org/details/The_Radiant) | http://creativecommons.org/licenses/by/3.0/ | test |
| [Thomas Park- Endless Dub Generation 1122022 [treetrunk 773] - Thomas Park](https://archive.org/details/ThomasParkEndlessDubGeneration1122022) | https://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Scott Lawlor, EugeneKha and Mister Vapor- Three Moons [treetrunk 305] - Scott Lawlor, EugeneKha and Mister Vap](https://archive.org/details/Three_Moons) | http://creativecommons.org/licenses/by-nd/3.0/ | train |
| [Thomas Park (with Brian Eno)- Thursday At Dusk [treetrunk 762]](https://archive.org/details/ThursdayAtDusk) | https://creativecommons.org/licenses/by-sa/4.0/ | train |
| [力が強くて凶暴 - Yukiga Futte Uresii](https://archive.org/details/Tikaraga_Tuyokute_Kyoubou) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Tim Blechmann - Live In Changchun - Tim Blechmann](https://archive.org/details/TimBlechmann-LiveInChangchun) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Sine Tempore 3 - Tim Blechmann](https://archive.org/details/TimBlechmann-SineTempore3) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Meat Force - Trick Turner - Meat Force](https://archive.org/details/TrickTurner) | http://creativecommons.org/publicdomain/zero/1.0/ | train |
| [Trom Ni Cuum - Yukiga Futte Uresii](https://archive.org/details/TromNiCuum) | http://creativecommons.org/licenses/by/2.1/jp/ | train |
| [(UT 2) ZOG - Sola Scriptura - ZOG](https://archive.org/details/UT2_Sola_Scriptura) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Uguisuinai - Yukiga Futte Uresii](https://archive.org/details/Uguisuinai) | http://creativecommons.org/licenses/by/2.1/jp/ | train |
| [後ろの正面ダークイエロー - Yukiga Futte Uresii](https://archive.org/details/UsironoSyoumenDarkYellow) | http://creativecommons.org/licenses/by/4.0/ | train |
| [Usuguraakarui - Yukiga Futte Uresii](https://archive.org/details/Usuguraakarui) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Victor Eleazer_Cthulu - Victor Eleazer](https://archive.org/details/VictorEleazer_cthulu) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Thomas Park- Viral Threat [treetrunk 507] - Thomas Park](https://archive.org/details/Viral_Threat) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Watasiwo　Wasuretano　Yurusanaiwa - Yukiga Futte Uresii](https://archive.org/details/WatWasYurusanaiwa) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Wax Clip - Yukiga Futte Uresii](https://archive.org/details/WaxClip) | http://creativecommons.org/licenses/by/2.1/jp/ | train |
| [Week 01 - House Laundry - loopool / Jean-Paul Garnier](https://archive.org/details/Week01) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 09 - Morning Hygiene - loopool / Jean-Paul Garnier](https://archive.org/details/Week09-MorningHygiene) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 10 - Skaters - loopool / Jean-Paul Garnier](https://archive.org/details/Week10-Skaters) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 16 - Echo Park Lake - loopool / Jean-Paul Garnier](https://archive.org/details/Week16-EchoParkLake) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 17 - Children - loopool / Jean-Paul Garnier](https://archive.org/details/Week17-Children) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 26 - L.A. at Night - loopool / Jean-Paul Garnier](https://archive.org/details/Week26-L.a.AtNight) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 31 - Ice Cream Truck - loopool / Jean-Paul Garnier](https://archive.org/details/Week31-IceCreamTruck) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 36 - Airplane Meal - loopool / Jean-Paul Garnier](https://archive.org/details/Week36-AirplaneMeal) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 37 - Library - loopool / Jean-Paul Garnier](https://archive.org/details/Week37-Library) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 39 - Paris at Night - loopool / Jean-Paul Garnier](https://archive.org/details/Week39-ParisAtNight) | http://creativecommons.org/licenses/by/3.0/ | test |
| [Week 40 - Paris in the Morning - loopool / Jean-Paul Garnier](https://archive.org/details/Week40-ParisInTheMorning) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 43 - Spark Chamber - loopool / Jean-Paul Garnier](https://archive.org/details/Week43-SparkChamber) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 44 - Gardners - loopool / Jean-Paul Garnier](https://archive.org/details/Week44-Gardners) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 45 - Broken Sink - loopool / Jean-Paul Garnier](https://archive.org/details/Week45-BrokenSink) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Week 52 - Tape Recorder - loopool / Jean-Paul Garnier](https://archive.org/details/Week52-TapeRecorder) | http://creativecommons.org/licenses/by/3.0/ | test |
| [Woofpac EP - Deadman & Digi Hartatak](https://archive.org/details/WoofpacEp) | http://creativecommons.org/licenses/by/3.0/us/ | train |
| [Thomas Park With Joshua Shaffer- Words And Music About Generative [treetrunk 622] - Thomas Park With Joshua Sh](https://archive.org/details/WordsAndMusicAboutGenerative) | https://creativecommons.org/licenses/by/4.0/ | train |
| [XXo/Dv! - Yukiga Futte Uresii](https://archive.org/details/XXo_Dv) | https://creativecommons.org/licenses/by/4.0/ | train |
| [XAVIER CORBERA - EL COMIAT - XAVIER CORBERA](https://archive.org/details/XavierCorberaElComiat) | https://creativecommons.org/licenses/by-nc/4.0/ | train |
| [呼ぶ声と足 (Yobukoeto Asi) - Yukiga Futte Uresii](https://archive.org/details/YobukoetoAsi) | http://creativecommons.org/licenses/by/3.0/ | train |
| [a house in iceland - MAHOGANY](https://archive.org/details/ZA0016) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [A Madness In Alice - Swamp Donkey & Dead By Hanging](https://archive.org/details/a-madness-in-alice) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | test |
| [A Rainy Night - Jazzaria.com](https://archive.org/details/a-rainy-night) | http://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [no word for art - x-flow](https://archive.org/details/abdicate_cellcontextsonicflow0606_05) | http://creativecommons.org/licenses/by-nc-sa/2.5/ | test |
| [[at090] La Culture C'est comme la Confiture Moins On En A Plus On Létale - David Area, Tomás Gris, Guillermo T](https://archive.org/details/at090_AreaGrisTorres_04_LaConfiture) | http://creativecommons.org/licenses/by-nc-sa/4.0/ | train |
| [Supernaculum - Akashic Crow's Nest](https://archive.org/details/bof041) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Tree Helicopter - The Numbest Station - Tree Helicopter](https://archive.org/details/bof048) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Scott Lawlor - Dark Mind - Scott Lawlor](https://archive.org/details/bof050) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Scott Lawlor - The Absence of Light Contains The Shadow of Loss - Scott Lawlor](https://archive.org/details/bof065) | http://creativecommons.org/licenses/by/3.0/ | test |
| [Grove Of Whispers - The Wind From Nowhere - John Tocher](https://archive.org/details/bof072) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Crystal Dreams - Tea Drones - Crystal Dreams](https://archive.org/details/bof075) | http://creativecommons.org/licenses/by/3.0/ | train |
| [I Wanna Buy You a New Screen Door - Heather Twatchops](https://archive.org/details/brennanworldwidescreen) | http://creativecommons.org/licenses/by-sa/4.0/ | train |
| [The Seven Sea's Devil [EP] - Capt'N CY4N](https://archive.org/details/capt-n-cy-4-n-mechanical-kraken) | None | train |
| [CARTOGRAFIA DEL CAOS - CARTOGRAFIA DEL CAOS](https://archive.org/details/cartografiaDelCaos) | http://creativecommons.org/licenses/by-nc/3.0/ | train |
| [inadequate - inadequate](https://archive.org/details/catplayground-inadequate) | None | train |
| [The Industrialism - Inconsequential Hallucinations [chase hs 06] - The Industrialism](https://archive.org/details/chasehs06) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Choke You Out - Deadman & Digi Hartatak](https://archive.org/details/chokeyouout) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Chromatibach - Jazzaria.com](https://archive.org/details/chromatibach) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | test |
| [Chronologically - Jazzaria.com](https://archive.org/details/chronologically) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [(Label) Circular읏 Discography - Circular읏](https://archive.org/details/circular-archive-discography) | None | train |
| [cloudcycle/cloud.1 - mauxuam](https://archive.org/details/cloudcycle-cloud1) | http://creativecommons.org/licenses/by-nc-sa/4.0/ | train |
| [Coleco Adult Uprising - Deadman & Digi Hartatak](https://archive.org/details/colecoadultuprising) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Creator Triple Theater - Deadman & Digi Hartatak](https://archive.org/details/creator_triple_theater_244) | http://creativecommons.org/licenses/by/3.0/ | train |
| [CRÓ! - PERA - CRÓ!](https://archive.org/details/croPera) | http://creativecommons.org/licenses/by-nc/3.0/ | train |
| [[deepx253LL] DeepDubing - Atmospheric Shadow - Deep-X Recordings](https://archive.org/details/deepx253LL) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [Demotic March - Jazzaria.com](https://archive.org/details/demotic-march) | http://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [derivative works - hanahata](https://archive.org/details/derivative-works) | https://creativecommons.org/licenses/by-sa/4.0/ | train |
| [Diagonally Opposing Eyebrows - Jazzaria.com](https://archive.org/details/diagonally-opposing-eyebrows) | http://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [dm001 - Jukka-Pekka Kervinen + August Traeger : Tracing Constructs - Jukka-Pekka Kervinen + August Traeger](https://archive.org/details/digitalminimum_dm001) | http://creativecommons.org/licenses/by/4.0/ | train |
| [DISCORDCORE - DJ Poop](https://archive.org/details/discordcore-1) | https://creativecommons.org/licenses/by-nc-sa/4.0/ | train |
| [Beautiful World - Derek Clegg](https://archive.org/details/diymARO4) | http://creativecommons.org/licenses/by-nc-nd/3.0/us/ | train |
| [eight - Various Artists](https://archive.org/details/diymVA08) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [IOK-1 - Sensorisk Deprivation - IOK-1](https://archive.org/details/dna_119_iok-1_sensorisk_deprivation) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Xalm Retribution - The Man With The Red Face - Xalm Retribution](https://archive.org/details/dna_151_xalm_retribution_the_man_with_the_red_face) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Igl00 - Untitled Scenes II - Igl00](https://archive.org/details/dna_158_igl00_untitled_scenes_ii) | http://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Anatoly Khvostishko - лабиринт сна, часть 1 (slumber labyrinth, part 1) - Anatoly Khvostishko](https://archive.org/details/dna_192_anatoly_khvostishko_slumber_labyrinth_part_1) | http://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Anatoly Khvostishko - лабиринт сна, часть 2 (slumber labyrinth, part 2) - Anatoly Khvostishko](https://archive.org/details/dna_193_anatoly_khvostishko_slumber_labyrinth_part_2) | http://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Arcane Waves - Malfunction - Arcane Waves](https://archive.org/details/dna_195_arcane_waves_malfunction) | http://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Bortom Reparation - Infrarod Portal-1 - Bortom Reparation](https://archive.org/details/dna_98_bortom_reparation_infrarod_portal_1) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Don't Feed the Trolls - Digi Hartatak](https://archive.org/details/dontfeedthetrolls) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Dr. NoiseM - The CDr A-B-C: M - Dr. NoiseM Tapes](https://archive.org/details/dr.-noisem-the-cdr-a-b-c-m) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Dr. NoiseM - The CDr A-B-C: P - Dr. NoiseM Tapes](https://archive.org/details/dr.-noisem-the-cdr-a-b-c-p) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Dr. NoiseM - The CDr A-B-C: V - Dr. NoiseM Tapes](https://archive.org/details/dr.-noisem-the-cdr-a-b-c-v) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Drone Note Samba - Jazzaria.com](https://archive.org/details/drone-note-samba) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Drone Music - Dan Lizard](https://archive.org/details/dronemusic) | http://creativecommons.org/licenses/by-nc-sa/4.0/ | train |
| [Thomas Park And Jon Shuemaker- Dusty Paintings And Nostalgic Timbres [treetrunk 817] - Thomas Park and Jon Shu](https://archive.org/details/dusty-paintings-and-nostalgic-timbres-by-jonathon-shumaker-and-thomas-park-06232025) | https://creativecommons.org/publicdomain/mark/1.0/ | train |
| [3pr(iii)13ses - David Oppetit, Vincent Pourchaire, MZ-N710](https://archive.org/details/earsheltering122) | https://creativecommons.org/licenses/by-nc-sa/4.0/ | train |
| [[Eg0_022] Tongues falling from an opened sky EP - Pura Sombar](https://archive.org/details/eg0_022) | http://creativecommons.org/licenses/by/4.0/ | train |
| [[Eg0_044] DMC and Tilil Pocket Orchestra - DMC and Kecap Tilil](https://archive.org/details/eg0_044) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [[Eg0_074] Ed End & TTWOSS : The Raven - Ed End & Thanato Twist with Oleg's Sound System](https://archive.org/details/eg0_074) | http://creativecommons.org/licenses/by-nc-sa/3.0/fr/ | train |
| [[Eg0_090] Tak Eniwa Sgormi](https://archive.org/details/eg0_090) | http://creativecommons.org/publicdomain/zero/1.0/ | train |
| [[Eg0_104] Digital Mass : Vacant Vision - Digital Mass](https://archive.org/details/eg0_104) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [[Eg0_121] < UNUNE > : Movements In Decay - < UNUNE >](https://archive.org/details/eg0_121) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [[Eg0_139] Ayato & Naoki Ishida : Red_control rec​.​played - Ayato & Naoki Ishida](https://archive.org/details/eg0_139) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [[Eg0_143] Sobria Ebrietas : Ashes of Light - Sobria Ebrietas](https://archive.org/details/eg0_143) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [Delikbeyin & 2Kutup : Susurrous EP - Delikbeyin & 2Kutup](https://archive.org/details/eg0_158) | http://creativecommons.org/licenses/by-nc-sa/4.0/ | test |
| [[Eg0_191] InO – Magali Albespy : 2017/2018 - InO - Magali Albespy](https://archive.org/details/eg0_191) | http://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Wataame Hazuki (乱雨羽月) & Filmy Ghost - El cementerio de los sueños - Wataame Hazuki (乱雨羽月) & Filmy Ghost](https://archive.org/details/el-cementerio-de-los-suenos) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Electric Carnival 2 - Digi Hartatak](https://archive.org/details/electric_carnival_2) | http://creativecommons.org/licenses/by/3.0/us/ | test |
| [Ementa Das Almas de Loriga (excerto) (2019) - Luis Antero](https://archive.org/details/ementadasalmasloriga2019excerto) | https://creativecommons.org/licenses/by-nd/4.0/ | train |
| [[ENDE019] Manifestevil - Dead But Not Buried- Unearthed Relics](https://archive.org/details/ende019-manifestevil-dead-but-not-buried) | None | train |
| [[ENDE031] V.A. - Senza Misura- Volume III](https://archive.org/details/ende031-va-senza-misura-vol-iii) | None | test |
| [[ENDE071] Noistruct - Nothing Is As Good As It Used To Be](https://archive.org/details/ende071-noistruct-nothing-is-as-good-as-it-used-to-be) | None | train |
| [[ENDE093] Vomitron Macdoom - Rekuring Nasengrasen](https://archive.org/details/ende093-vomitron-macdoom-rekuring-nasengrasen) | None | train |
| [[ENDE176] Mandark - Parasomnia](https://archive.org/details/ende176-mandark-parasomnia) | None | train |
| [[ENDE246] Erohypnos - Data Gods Orgasmic Swine](https://archive.org/details/ende246-erohypnos) | None | train |
| [[ENDE290] Spinecode - Paranorgasm](https://archive.org/details/ende290-spinecode-paranorgasm) | None | train |
| [[ENDE301] Batard Tronique - Mixtape Troniquologique](https://archive.org/details/ende301-batard-tronique-mixtape-troniquologique) | None | train |
| [[ENDE327] The Filth - Live at DJ Zeitgeist's 2004](https://archive.org/details/ende327-the-filth-live-at-dj-zeitgeists-2004) | None | train |
| [[ENDE421] Etdevagina - Regicide](https://archive.org/details/ende421-etdevagina-regicide) | None | train |
| [[ENDE454] Energy Commission - Live At Ya Ya's 2009 And Bonus Demos](https://archive.org/details/ende454-energy-commision-live-yayas-2009-plus-demos) | None | test |
| [[ENDE609] Boris Otterdam - Home Recordings- Vol. 1](https://archive.org/details/ende609-boris-otterdam-home-recordings-vol-1) | None | train |
| [[EPH038] NIGNUS -Dubstep animal (Ephedrin7") - Ephedrina's Crew](https://archive.org/details/eph038Nignus-DubstepAnimal7inch) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [Fabio Keiner - Book of JEU - Fabio Keiner](https://archive.org/details/fabio-keiner-book-of-jeu) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Unreleased Tracks. Volume 3. - Fellirium](https://archive.org/details/fellirium_unreleased_tracks_vol_3) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [File Under Toner - And Now, The End Is Near - File Under Toner](https://archive.org/details/file_under_toner_and_now) | http://creativecommons.org/publicdomain/zero/1.0/ | train |
| [Scrap Heap - Fixture - Scrap Heap](https://archive.org/details/fixture) | http://creativecommons.org/licenses/publicdomain/ | train |
| [Vic - Ugly Duck - Vic](https://archive.org/details/fm-29) | None | train |
| [vic - kletter pats boem! - vic](https://archive.org/details/fm-35) | None | train |
| [Forgotten Creation - Jazzaria.com](https://archive.org/details/forgotten-creation) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Free Bee - Jazzaria.com](https://archive.org/details/free-bee) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Gaza -Themes ( Where Western Humanity Went To Die) - Swamp Donkey](https://archive.org/details/gaza-themes-where-western-humanity-went-to-die) | https://creativecommons.org/publicdomain/mark/1.0/ | train |
| [x-zlif aka Hell - Shtorm. Welcome to Hell (2006-2007)](https://archive.org/details/gt1134_201907) | None | test |
| [[GT370] Boxing Day Special](https://archive.org/details/gt370BoxingDaySpecial) | http://creativecommons.org/publicdomain/zero/1.0/ | train |
| [[GT381] 4.09 - Hydrophobia](https://archive.org/details/gt3814.09-Hydrophobia) | http://creativecommons.org/publicdomain/zero/1.0/ | test |
| [[GT382] Alex Ischenkau - Dead - Alex Usiel Ischenkau](https://archive.org/details/gt382AlexIschenkau-Dead) | http://creativecommons.org/publicdomain/zero/1.0/ | test |
| [[GT453] Morbid Silence / Radio Noiseville / RMSS Systems Inc. - Chernobyl Nuclear Power Plant](https://archive.org/details/gt453ChernobylNuclearPowerPlant) | http://creativecommons.org/publicdomain/zero/1.0/ | train |
| [hOmeArtv.0.0.1.(oz008) - Massimo Croce](https://archive.org/details/hOmeArtv.0.0.1.oz008) | http://creativecommons.org/licenses/publicdomain/ | train |
| [HNR035 / Corroded Master / Forgotten Archives - Vince Gauthier](https://archive.org/details/hnr035) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | test |
| [Oriol Perucho - Así pasan 45 minutos - Oriol Perucho](https://archive.org/details/hr006) | http://creativecommons.org/licenses/publicdomain/ | train |
| [Kalimpong Trio - Washi Chiyogami [HR016] - Kalimpong Trio](https://archive.org/details/hr016) | http://creativecommons.org/licenses/publicdomain/ | train |
| [M&D - M&D [hr020] - M&D](https://archive.org/details/hr020) | http://creativecommons.org/licenses/publicdomain/ | train |
| [Breuss Arrizabalaga Quintet - Concert For Kowald [HR034] - Breuss Arrizabalaga Quintet](https://archive.org/details/hr034) | http://creativecommons.org/licenses/publicdomain/ | train |
| [File Under Toner - 45 RPM [HR045] - File Under Toner](https://archive.org/details/hr045) | http://creativecommons.org/licenses/publicdomain/ | train |
| [DEMO - Superelvis FAT Corruption - DEMO](https://archive.org/details/hr054) | http://creativecommons.org/licenses/publicdomain/ | train |
| [Adrián Juárez - San Pedro [HR055] - Adrián Juárez](https://archive.org/details/hr055) | http://creativecommons.org/licenses/publicdomain/ | train |
| [Ayankoko!!! - Red Rose And Two Moons [HR058] - Ayankoko!!!](https://archive.org/details/hr058) | http://creativecommons.org/licenses/publicdomain/ | train |
| [Resistance Emotional Mixes, vol 1 - File Under Toner](https://archive.org/details/hr069) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [nadia spier vs. nad spiro - eXtensions of you (vol. 1) - nadia spier vs. nad spiro](https://archive.org/details/hr084) | http://creativecommons.org/publicdomain/zero/1.0/ | train |
| [Antoni Robert - Train Pieces (Final Mix) - Antoni Robert](https://archive.org/details/hr089) | http://creativecommons.org/publicdomain/zero/1.0/ | train |
| [Hydra feat. Stereorent - Improvisions - Hydra feat Stereorent](https://archive.org/details/hr090) | http://creativecommons.org/publicdomain/zero/1.0/ | train |
| [Sesiones de improvisación Cajanegra - Esquizomachina / Bullet138](https://archive.org/details/improvisaCajanegra) | http://creativecommons.org/publicdomain/zero/1.0/ | train |
| [[ISOR021] About Sun Light - MaCu with God Pussy](https://archive.org/details/isor021AboutSunLight) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Chipmunk - Jazzaria.com](https://archive.org/details/jazzaria_chipmunk) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Thomas Park- King No Longer Nor Captain [treetrunk 820] - Thomas Park](https://archive.org/details/king-no-longer-nor-captain) | https://creativecommons.org/publicdomain/mark/1.0/ | train |
| [KIRA Discography - KIRA](https://archive.org/details/kira-discography) | None | train |
| [Iñaki Barrocal - Sun in my Mouth [khmst0069] - Iñaki Barrocal](https://archive.org/details/kmst0069-suninmymouth) | https://creativecommons.org/licenses/by-nc-sa/4.0/ | train |
| [Little Grateful Dan - Faykers](https://archive.org/details/little_grateful_dan) | http://creativecommons.org/licenses/by/3.0/us/ | train |
| [LoneR - Digi Hartatak](https://archive.org/details/loner) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Martim Arce - Desde las tripas - Martim Arce](https://archive.org/details/martim_arce-desde_las_tripas) | http://creativecommons.org/licenses/by-nc-sa/4.0/ | train |
| [Mean Mother Green - Deadman & Digi Hartatak](https://archive.org/details/meanmothergreen) | http://creativecommons.org/licenses/by/3.0/ | train |
| [messian_dread_-_consider_i_discomix_2007 - Messian Dread](https://archive.org/details/messian_dread_-_consider_i_discomix_2007) | http://creativecommons.org/licenses/by-nc-nd/3.0/nl/ | train |
| [Bits Is All There Is - Eskaei](https://archive.org/details/mfm11__eskaei_-_bits_is_all_there_is) | https://creativecommons.org/licenses/by-nd/4.0/ | train |
| [Minimal Ambient - Digi Hartatak](https://archive.org/details/minimalambient) | http://creativecommons.org/licenses/by/3.0/ | train |
| [mrmcq03 - Juliana Stein - Hide and Seek (Julianimatronic Remix)](https://archive.org/details/mrmcq03-julianastein-hideandseekjulianimatronicremix) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [mrmcq27 - Juliana Stein - A New Kind of Love - Juliana Stein](https://archive.org/details/mrmcq27-julianastein-anewkindoflove) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [Multitudes - Jazzaria.com](https://archive.org/details/multitudes) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [mystified - Nocturne [treetrunk015] - Thomas Park](https://archive.org/details/mystified_Nocturne) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Nuestros Ninos 12-21-2003](https://archive.org/details/nuestros-ninos-03-12-21) | None | train |
| [Nuestros Ninos 02-15-2004](https://archive.org/details/nuestros-ninos-04-02-15) | None | train |
| [oooi ooooof - Yukiga Futte Uresii](https://archive.org/details/oooiooooof) | http://creativecommons.org/licenses/by/4.0/ | train |
| [oooi ov ooooof - Yukiga Futte Uresii](https://archive.org/details/oooiovooooof) | http://creativecommons.org/licenses/by/4.0/ | train |
| [(Petroglyph140) Grove Of Whispers - The Everything - Grove Of Whispers](https://archive.org/details/petroglyph140GroveOfWhispers-TheEverything) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Pink Freud - Digi Hartatak](https://archive.org/details/pinkfreud) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Thomas Park- Popmuzik [treetrunk 487] - Thomas Park](https://archive.org/details/popmuzik2020) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [En040 Primo Gabbiano_Porn Senglar - Primo Gabbiano](https://archive.org/details/primoGabbiano_PornSenglar) | http://creativecommons.org/licenses/by-nc/3.0/ | train |
| [Ysabel - Quarto Nove Ilda. feat. Fernanda Bragança](https://archive.org/details/quarto-nove-ilda-feat.-fernanda-braganca-ysabel-single-xi-ii-mmxxi-ie) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Race Against Socks - Jazzaria.com](https://archive.org/details/race-against-socks) | http://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Da Mihi Manum - Simon Chadwick](https://archive.org/details/raretunes_204_da-mihi-manum) | http://creativecommons.org/licenses/by-nc-sa/2.5/scotland/ | train |
| [Reels - Bella McNab's Dance Band](https://archive.org/details/raretunes_437_reels-1a) | http://creativecommons.org/licenses/by-nc-sa/2.5/scotland/ | train |
| [BarryTones 2010s - BarryTones](https://archive.org/details/retrospecrecords05) | http://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [[rj002] Bordo - Brzmi wewnątrz (1999) - Bordo](https://archive.org/details/rj002-bordo-brzmi-wewnatrz-1999) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Seamonkeys - Digi Hartatak](https://archive.org/details/seamonkeys) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Sex Worker Rights](https://archive.org/details/sex-worker-rights) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Acid Attack - S.Ahola](https://archive.org/details/siko-032) | http://creativecommons.org/licenses/by-nd-nc/1.0/fi/ | test |
| [Spring Equinox - Fellirium](https://archive.org/details/spring-equinox) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [[STC001] Lusruta & TGBTS - Rivers Of Ashes - Lusruta & The Ghost Between The Strings](https://archive.org/details/stc001) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [Thomas Park- The Easiest [treetrunk 548] - Thomas Park](https://archive.org/details/the-easiest) | http://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Thomas Park And Jon Shuemaker- The Sadness In The Riddle [treetrunk 822] - Thomas Park and Jon Shuemaker](https://archive.org/details/the-sadness-in-the-riddle) | https://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Evergreen- The Wanderer's Perpetual Drift [treetrunk 830] - Jon Christopher and Thomas Park](https://archive.org/details/the-wanderers-perpetual-drift) | https://creativecommons.org/licenses/by/4.0/ | test |
| [Thomas Park- Three Local Pianos In A Day [treetrunk 776] - Thomas Park](https://archive.org/details/threelocalpianosina-day) | https://creativecommons.org/publicdomain/mark/1.0/ | train |
| [Sum-1 - Burnt Toast For Breakfast - Tobias Peterson](https://archive.org/details/tm-sum1-burnt-toast) | http://creativecommons.org/licenses/by/3.0/ | train |
| [Lezet - Meld 2](https://archive.org/details/tng1043) | http://creativecommons.org/licenses/by-nc-nd/3.0/ | train |
| [undefined label: rcomplexbrain - serpent - rcomplexbrain](https://archive.org/details/undefined-label-rcomplexbrain-serpent) | None | train |
| [V/A - Dark Ambient Fields - Internet Daemon Netlabel](https://archive.org/details/v-a-dark-ambient-fields) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [V/A - Gothic Spectra VII - Gothic Spectra](https://archive.org/details/v-a-gothic-spectra-vii) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | test |
| [V/A - A Witch House Music Tribute to Twin Peaks - Internet Daemon Netlabel](https://archive.org/details/v-a-tribute-to-twin-peaks) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Vacant Cloister - jlowery](https://archive.org/details/vacantcloister) | http://creativecommons.org/licenses/by/3.0/ | train |
| [[vau015] mtml - mtml](https://archive.org/details/vau015) | None | train |
| [For Seasons - vvglyy](https://archive.org/details/vvglyy-for-seasons) | None | train |
| [Warmups - Jazzaria.com](https://archive.org/details/warmups) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [Mystified & Saluki Regicide - Razor Pluvia [wh225] - C.P McDill](https://archive.org/details/wh225) | http://creativecommons.org/licenses/by-nc-nd/3.0/us/ | train |
| [Grove of Whispers - The World Carried On [wh253] - John Tocher](https://archive.org/details/wh253) | http://creativecommons.org/licenses/by/3.0/us/ | train |
| [Grove of Whispers - Against the Stream [wh265] - John Tocher](https://archive.org/details/wh265) | http://creativecommons.org/licenses/by/3.0/ | test |
| [Wivresse - Dark Nest - Wivresse](https://archive.org/details/wivresse-dark-nest) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [WP - Emptiness (EP) (2019) - WP](https://archive.org/details/wp-emptiness-ep) | https://creativecommons.org/licenses/by-nc-nd/4.0/ | train |
| [yvlc Discography - yvlc](https://archive.org/details/yvlc-discography_) | None | train |
| [.C. Works - Cornucopia](https://archive.org/details/zero005) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [Portable Noise Kremator - Portable Noise Kremator](https://archive.org/details/zero009CB) | http://creativecommons.org/licenses/by-nc-sa/3.0/ | train |
| [Various Artists - Zeromoon Sampler III: An Explanation of Difficult Music - various artists](https://archive.org/details/zero057) | http://creativecommons.org/licenses/by-nc-sa/2.0/ | test |
| [Five Movements for Six String Players - Third Object Orchestra](https://archive.org/details/zero108) | http://creativecommons.org/licenses/by-nc-sa/3.0/us/ | train |
