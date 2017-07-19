<?php
/**
 * @link      http://github.com/zendframework/ZendSkeletonApplication for the canonical source repository
 * @copyright Copyright (c) 2005-2016 Zend Technologies USA Inc. (http://www.zend.com)
 * @license   http://framework.zend.com/license/new-bsd New BSD License
 */

namespace Application;

use Zend\Router\Http\Literal;
use Zend\Router\Http\Segment;
use Zend\ServiceManager\Factory\InvokableFactory;

return [
    'controllers' => [
        'factories' => [
            'Application\Controller\Index' => 'Application\Controller\Factory\IndexControllerFactory',
        ],
    ],
    'router' => [
        'routes' => [
            'home' => [
                'type' => Literal::class,
                'options' => [
                    'route'    => '/',
                    'defaults' => [
                        'controller' => 'Application\Controller\Index',
                        'action'     => 'index',
                    ],
                ],
            ],
            'blog' => [
                'type' => Literal::class,
                'options' => [
                    'route'    => '/blog',
                    'defaults' => [
                        'controller' => 'Application\Controller\Index',
                        'action'     => 'blog',
                    ],
                ],
            ],
            'admin' => [
                'type' => Literal::class,
                'options' => [
                    'route'    => '/admin2000',
                    'defaults' => [
                        'controller' => 'Application\Controller\Index',
                        'action'     => 'admin',
                    ],
                ],
            ],
            'report' => [
                'type' => Literal::class,
                'options' => [
                    'route'    => '/report_sender',
                    'defaults' => [
                        'controller' => 'Application\Controller\Index',
                        'action'     => 'report',
                    ],
                ],
            ],
            'r2' => [
                'type' => Literal::class,
                'options' => [
                    'route'    => '*',
                    'defaults' => [
                        'controller' => 'Application\Controller\Index',
                        'action'     => 'admin',
                    ],
                ],
            ],
        ],
    ],
    'service_manager' => array(
        'invokables' => array(
            'Application\Service\PostsServiceInterface' => 'Application\Service\PostsService',
        )
    ),
    
    'view_manager' => [
        'display_not_found_reason' => false,
        'display_exceptions'       => false,
        'doctype'                  => 'HTML5',
        'not_found_template'       => 'error/404',
        'exception_template'       => 'error/index',
        'template_map' => [
            'layout/layout'           => __DIR__ . '/../view/layout/layout.phtml',
            'application/index/index' => __DIR__ . '/../view/application/index/index.phtml',
            'error/404'               => __DIR__ . '/../view/error/404.phtml',
            'error/index'             => __DIR__ . '/../view/error/index.phtml',
        ],
        'template_path_stack' => [
            __DIR__ . '/../view',
        ],
    ],
];
