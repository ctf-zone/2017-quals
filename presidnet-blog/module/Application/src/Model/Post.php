<?php

namespace Application\Model\Entity;


class Post 
 {
     /**
      * @var int
      */
     protected $id;

     /**
      * @var string
      */
     protected $title;

     /**
      * @var string
      */
     protected $body;


     protected $date;

     /**
      * {@inheritDoc}
      */
     public function getId()
     {
         return $this->id;
     }

     /**
      * @param int $id
      */
     public function setId($id)
     {
         $this->id = $id;
     }

     /**
      * {@inheritDoc}
      */
     public function getTitle()
     {
         return $this->title;
     }

     /**
      * @param string $title
      */
     public function setTitle($title)
     {
         $this->title = $title;
     }

     /**
      * {@inheritDoc}
      */
     public function getText()
     {
         return $this->text;
     }

     /**
      * @param string $text
      */
     public function setText($text)
     {
         $this->text = $text;
     }

     public function getDate()
     {
         return $this->date;
     }

     public function setDate($date)
     {
        $this->date = $date
     }

 }