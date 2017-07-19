<?php
/**
 * @link      http://github.com/zendframework/ZendSkeletonApplication for the canonical source repository
 * @copyright Copyright (c) 2005-2016 Zend Technologies USA Inc. (http://www.zend.com)
 * @license   http://framework.zend.com/license/new-bsd New BSD License
 */

namespace Application;
use Zend\ModuleManager\Feature\ServiceProviderInterface;
use Application\Model\PostsTable;
use Zend\Mvc\MvcEvent;
use Zend\Session\SessionManager;
use Zend\Session\Container;



class Module implements ServiceProviderInterface
{
    const VERSION = '3.0.3-dev';
    public function onBootstrap(MvcEvent $event)
    {
        $application = $event->getApplication();
        $serviceManager = $application->getServiceManager();
        $sessionManager = $serviceManager->get(SessionManager::class);

        // $config = $event->getApplication()
        //           ->getServiceManager()
        //           ->get('Configuration');

        // $sessionConfig = new SessionConfig();
        // $sessionConfig->setOptions($config['session']);
        // $sessionManager = new SessionManager($sessionConfig);
        // $sessionManager->start();
        // $application = $event->getApplication();
        // $svcMgr = $application->getServiceManager();

        // //  Instantiate the session manager and
        // //  make it the default one
        // //
        // $sessionManager = $svcMgr->get(SessionManager::class);
    }

    public function getConfig()
    {
        return include __DIR__ . '/../config/module.config.php';
    }
    public function getServiceConfig() {
        // return array(
        //     'factories' => array(
        //         'Posts\Model\PostsTable' => function($sm) {
        //             $dbAdapter = $sm->get('Zend\Db\Adapter\Adapter');
        //             $table = new PostsTable($dbAdapter);
        //             return $table;
        //         },
        //     ),
        // );
        return array(
            'controllers' => array(
                'factories' => [
                    'Application\Controller\IndexController' => 'Application\Controller\Factory\IndexControllerFactory',
                ]
            ),
            'factories' => array(
                'Application\Model\PostsTable' =>  function($sm) {
                $tableGateway = $sm->get('PostsTable');
                $table = new PostsTable($tableGateway);
                return $table;
            }
            )
        );
    }
}
