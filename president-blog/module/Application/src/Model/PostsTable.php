<?php

namespace Posts\Model;

use Zend\Db\Adapter\Adapter;
use Zend\Db\TableGateway\AbstractTableGateway;

class PostsTable extends AbstractTableGateway {

    protected $table = 'posts';

    public function __construct(Adapter $adapter) {
        $this->adapter = $adapter;
    }

    public function fetchAll() {
        $resultSet = $this->select(function (Select $select) {
                    $select->order('created ASC');
                });
        // $entities = array();
        // foreach ($resultSet as $row) {
        //     $entity = new Entity\StickyNote();
        //     $entity->setId($row->id)
        //             ->setNote($row->note)
        //             ->setCreated($row->created);
        //     $entities[] = $entity;
        // }
        return array();
    }

}
