function toggleHeart() {
    $(".heart").on("click", function () {
        //   let storyNum = $(this).parent().attr('id')
        //   let story = storyList.stories.filter(x => x.storyId === storyNum)
        if (this.innerText === '♡') {
            // currentUser.addFavorite(story)
            this.innerText = '♥';
            pk = $(this).parent().attr('id')
            // this.classList.add("fav")
        } else {
            this.innerText = '♡';
            // let favStory = story[0]
            // currentUser.removeFavorite(favStory)
            // this.classList.remove("fav")
        }
    })
}
window.onload = function () {
    toggleHeart()
}; 