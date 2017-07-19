<?php
namespace Application\Service;



class PostsService implements PostsServiceInterface
{
    protected $data = array(
        array(
            'id'    => 1,
            'title' => 'Hello World #1',
            'text'  => 'This is our first blog post!'
        )
    );
    protected $postMapper;

    // public function __construct(PostMapperInterface $postMapper)
    // {
    //     $this->postMapper = $postMapper;
    // }




    public function findAllPosts()
    {
        return "array()";
        // return $this->postMapper->findAll();
    }
}