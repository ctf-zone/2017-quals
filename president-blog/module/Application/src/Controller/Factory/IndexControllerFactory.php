<?php

namespace Application\Controller\Factory;


use Interop\Container\ContainerInterface;
use Zend\ServiceManager\Factory\FactoryInterface;
use Zend\Db\Adapter\Adapter;
use Zend\Session\SessionManager;

use Application\Controller\IndexController;
use Application\Model\PostsTable;
use Zend\Session\Container;


class IndexControllerFactory implements FactoryInterface
{
    public function __invoke(ContainerInterface $container, $requestedName, array $options = null)
    {
        $config = $container->get('config');
        $sm = $container->get(SessionManager::class);
        $sm->start();
        Container::setDefaultManager($sm);

        $containter = new Container('ContainerNamespace', $sm);

        $db = new Adapter($config['db']);
        return new IndexController($db, $sm, $containter);
    }

}
