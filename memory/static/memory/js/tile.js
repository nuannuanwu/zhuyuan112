$(function() {
	//初始化瀑布流
    var $container = $('.thumbnails');
    $container.imagesLoaded(function(){
        $container.masonry({
            columnWidth: function( containerWidth ) {
                return containerWidth / 5;
              },
            itemSelector : '.tile',
            //columnWidth: 234,
            gutterWidth: 0,
            isAnimated: true,
            animationOptions: {
                duration: 400,
                easing: 'linear',
                queue: false
            }
        });
    });
	//分页自动加载，新增内容瀑布流化
    $container.infinitescroll({
        navSelector  : '#pagination',    // selector for the paged navigation
        nextSelector : $('#pagination li.active').next().children('a'),  // selector for the NEXT link (to page 2)
        itemSelector : '.tile',     // selector for all items you'll retrieve
        debug        : true,
        loading: {
            finishedMsg: "没有更多页面了",
            //img: 'http://i.imgur.com/6RMhx.gif'
			//img: '{{ STATIC_URL }}memory/img/6RMhx.gif'
			img: 'http://oss.aliyuncs.com/zhuyuan/icon/6RMhx.gif'
        }
    },
    // trigger Masonry as a callback
    function( newElements ) {
        // hide new items while they are loading
        var $newElems = $( newElements ).css({ opacity: 0 });
        $( newElements ).find('[rel=namecard]').namecard();
        // ensure that images load before adding to masonry layout
        $newElems.imagesLoaded(function(){
            // show elems now they're ready
            $newElems.animate({ opacity: 1 });
            $container.masonry( 'appended', $newElems, true );
        });
    });


    $tiles = $container.find("li.tile");
	if( /Android|iPhone|iPad/i.test(navigator.userAgent) ){
		  //handheld
		}else{
		  $tiles.live("mouseover", function(e){
          $(this).find('.actions').show();
             })
        .live("mouseout", function(e) {
        $(this).find(".actions").hide();
      });
    }
   
    // $tiles.find(".actions .btn.comment").live("click",function(e){
    //     $form = $('#comment-form-'+$(this).data('id'));
    //     $form.toggle();
    //     events = $form.data("events");
    //     if (!events || events.submit.length <=0) {
    //         $form.submit(function(e){
    //             e.preventDefault();
    //             url = $form.attr('action');
    //             $.post(url, $form.serialize(), function(data,st){
    //                 console.log(st,data);
    //             });
    //         });
    //     }
    // });


    /* tile_view */
    $('.kDetail-bar .comment').on('click', function(e){
        $('#comment-form .controls textarea#id-comment').focus();
    });

    $("#comment-form").submit(function(){
        $text = $(this).find(".controls textarea#id-comment");
        text_len = $.trim($text.val()).length;
        if (text_len)
            return true;
        else {
            $text.focus();
            return false;
        }
    });

    $("button.likeable:not(.disabled)").live("click",function(e){
        $btn_like = $(this);
        url = $btn_like.data("href");
        id = $btn_like.data("id");
        $i = $btn_like.find("i");
        $btn_like.addClass("disabled");
        $.post(url,{"id": id},function(data, status){
            if(status != "success")
                return false;
            if (data.liked) {
                $i.addClass("like");
                
                $btn_like.find('span').html("取消喜欢");
            } else {
                $i.removeClass("like");
                
                $btn_like.find('span').html("喜欢");
            }
            $btn_like.removeClass("disabled");
        },"json");
    });

// 2013-1-25

});
