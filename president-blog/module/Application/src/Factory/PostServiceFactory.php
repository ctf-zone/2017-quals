<?php
namespace Appliaction\Factory;

use Appliaction\Service\PostService;
use Zend\ServiceManager\FactoryInterface;
use Zend\ServiceManager\ServiceLocatorInterface;
use Interop\Container\ContainerInterface;

class PostServiceFactory implements FactoryInterface
{
    /**
     * Create service
     *
     * @param ServiceLocatorInterface $serviceLocator
     * @return mixed
     */
    public function createService(ServiceLocatorInterface $serviceLocator)
    {
        return new PostService(
            $serviceLocator->get('Appliaction\Mapper\PostMapperInterface')
        );
    }
    public function __invoke(ContainerInterface $container, $requestedName, array $options = null)
    {
        // get your dependency
        $postService = $container->get(AlbumTable::class),;
        // inject it int the constructor
        return new IndexController($postService);
    }
}